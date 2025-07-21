import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_model, crud_map
from app.services.dqn_agent import DQNAgent
from app.services.rl_environment import My2DEnv, Size, GridPosition
from app.database.session import get_db
import torch
import asyncio
import time

router = APIRouter()


@router.websocket("/train_dqn/{model_id}/{map_id}")
async def websocket_dqn_train(websocket: WebSocket, model_id: str, map_id: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    map_schema = await crud_map.get_map_by_map_id(map_id, db)
    model_schema = await crud_model.get_model_by_model_id(model_id, db)

    if not map_schema:
        await websocket.close(code=4004, reason="Map not found")
        return

    if not model_schema:
        await websocket.close(code=4004, reason="Model not found")
        return

    env = My2DEnv(
        grid_size=Size(map_schema.map_size[0], map_schema.map_size[1]),
        walls=[GridPosition(wall.x, wall.y) for wall in map_schema.wall_list],
        traps=[GridPosition(trap.x, trap.y) for trap in map_schema.trap_list],
        bits=[GridPosition(bit.x, bit.y) for bit in map_schema.bit_list],
        goal=GridPosition(map_schema.exit_pos.x, map_schema.exit_pos.y),
        agent_start=GridPosition(map_schema.agent_pos.x, map_schema.agent_pos.y),
        max_steps=map_schema.max_steps
    )
    action_dim = 4
    agent = DQNAgent(
        action_dim=action_dim,
        state_dim=env.max_bits + 2,
        device=device,
        learning_rate=model_schema.learning_rate,
        batch_size=model_schema.batch_size,
        gamma=model_schema.gamma,
        epsilon_start=model_schema.epsilon_start,
        epsilon_min=model_schema.epsilon_min,
        epsilon_decay=model_schema.epsilon_decay,
        update_target_every=model_schema.update_target_every
    )

    model_path = model_schema.model_url
    if model_path and os.path.exists(model_path):
        agent.model.load_state_dict(torch.load(model_path, map_location=device))
        agent.target.load_state_dict(agent.model.state_dict())
        await websocket.send_json({"event": "model_loaded", "model_url": model_path})
    else:
        await websocket.send_json({"event": "model_created"})

    try:
        episode = 0
        start = time.time()
        while True:
            state, _ = env.reset()
            total_reward = 0
            reward = 0
            step = 0
            done = False
            while not done:
                action = agent.select_action(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                agent.store(state, action, reward, next_state, done)
                loss = agent.train_step()
                agent.update_epsilon()
                state = next_state
                total_reward += reward
                step += 1

                # 여기서는 별도의 try-except 없이 바로 전송
                await asyncio.sleep(0)
                await websocket.send_json({
                    "event": "step",
                    "episode": episode,
                    "step": step,
                    "state": state.tolist(),
                    "action": action,
                    "reward": reward,
                    "total_reward": total_reward,
                    "loss": loss,
                    "epsilon": agent.epsilon,
                    "terminated": terminated,
                    "truncated": truncated
                })

                env.render()
                if terminated or truncated:
                    break

            if episode % agent.update_target_every == 0:
                agent.update_target_network()

            if reward >= 1.0:
                await websocket.send_json(
                    {"event": "episode_success", "episode": episode, "total_reward": total_reward})
                break

            episode += 1
        end = time.time()

        torch.save(agent.model.state_dict(), model_path)
        await asyncio.sleep(0)
        await websocket.send_json({"event": "model_saved", "model_url": model_path})
        print(f"Training completed in {end - start:.2f} seconds, total episodes: {episode + 1}", flush=True)

    except WebSocketDisconnect:
        print("WebSocket disconnected by client", flush=True)
    # 추가 close 불필요
    except Exception as e:
        print(f"Other error: {e}", flush=True)
    try:
        await websocket.close()
    except RuntimeError:
        print("Cannot close websocket, already closed", flush=True)


@router.websocket("/train_dqn/{model_id}/{map_id}/loop")
async def websocket_dqn_train_loop(websocket: WebSocket, model_id: str, map_id: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    map_schema = await crud_map.get_map_by_map_id(map_id, db)
    model_schema = await crud_model.get_model_by_model_id(model_id, db)

    if not map_schema:
        await websocket.close(code=4004, reason="Map not found")
        return

    if not model_schema:
        await websocket.close(code=4004, reason="Model not found")
        return

    env = My2DEnv(
        grid_size=Size(map_schema.map_size[0], map_schema.map_size[1]),
        walls=[GridPosition(wall.x, wall.y) for wall in map_schema.wall_list],
        traps=[GridPosition(trap.x, trap.y) for trap in map_schema.trap_list],
        bits=[GridPosition(bit.x, bit.y) for bit in map_schema.bit_list],
        goal=GridPosition(map_schema.exit_pos.x, map_schema.exit_pos.y),
        agent_start=GridPosition(map_schema.agent_pos.x, map_schema.agent_pos.y),
        max_steps=map_schema.max_steps
    )
    action_dim = 4
    agent = DQNAgent(
        action_dim=action_dim,
        state_dim=env.max_bits + 2,
        device=device,
        learning_rate=model_schema.learning_rate,
        batch_size=model_schema.batch_size,
        gamma=model_schema.gamma,
        epsilon_start=model_schema.epsilon_start,
        epsilon_min=model_schema.epsilon_min,
        epsilon_decay=model_schema.epsilon_decay,
        update_target_every=model_schema.update_target_every
    )

    model_path = model_schema.model_url
    if model_path and os.path.exists(model_path):
        agent.model.load_state_dict(torch.load(model_path, map_location=device))
        agent.target.load_state_dict(agent.model.state_dict())
        await websocket.send_json({"event": "model_loaded", "model_url": model_path})
    else:
        await websocket.send_json({"event": "model_created"})

    try:
        episode = 0
        while True:
            state, _ = env.reset()
            total_reward = 0
            reward = 0
            step = 0
            done = False
            while not done:
                action = agent.select_action(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                agent.store(state, action, reward, next_state, done)
                loss = agent.train_step()
                agent.update_epsilon()
                state = next_state
                total_reward += reward
                step += 1

                # 여기서는 별도의 try-except 없이 바로 전송
                await websocket.send_json({
                    "event": "step",
                    "episode": episode,
                    "step": step,
                    "state": state.tolist(),
                    "action": action,
                    "reward": reward,
                    "total_reward": total_reward,
                    "loss": loss,
                    "epsilon": agent.epsilon,
                    "terminated": terminated,
                    "truncated": truncated
                })
                await asyncio.sleep(0)

                env.render()
                if terminated or truncated:
                    break

            if episode % agent.update_target_every == 0:
                agent.update_target_network()

            if reward >= 1.0:
                await websocket.send_json(
                    {"event": "episode_success", "episode": episode, "total_reward": total_reward})
                torch.save(agent.model.state_dict(), model_path)
                await asyncio.sleep(0)
                await websocket.send_json({"event": "model_saved", "model_url": model_path})
            episode += 1

    except WebSocketDisconnect:
        print("WebSocket disconnected by client", flush=True)
    # 추가 close 불필요
    except Exception as e:
        print(f"Other error: {e}", flush=True)
    try:
        await websocket.close()
    except RuntimeError:
        print("Cannot close websocket, already closed", flush=True)
