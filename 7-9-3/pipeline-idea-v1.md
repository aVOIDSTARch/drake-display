# Draft 1 - July 9

Use a **continuous scalar field** (or vector field if each point has multiple values) plus a **discretized grid** for computation.

1) **Best math for the state**

- If values evolve smoothly over space/time: model it as a **partial differential equation (PDE)** on a 2D or 3D grid.
- If each point is updated by rules/equations and neighbors matter: use a **cellular / lattice field** or **finite-difference / finite-volume** scheme.
- If you need many changing equations, think in terms of:
  - **state field** \(u(x,y,t)\)
  - **operator-based updates** \(u_{t+\Delta t} = F(u_t, \nabla u_t, \dots)\)
  - possibly **stochastic fields** if there’s randomness.

For deformation in 3D, a **scalar density field** or **signed distance field (SDF)** is often best, because the renderer can turn it into geometry.

1) **Best code libraries / stack**
For speed, use a **GPU-first pipeline**.

- **Compute/update**
  - **CUDA** (NVIDIA) for fastest custom field updates
  - **OpenCL** or **Vulkan compute shaders** for broader GPU support
  - **WGPU/WebGPU** if you want modern cross-platform compute
  - **NumPy + Numba** for prototyping on CPU
  - **JAX** or **PyTorch** if the update rules are differentiable / ML-like

- **Storage**
  - **Contiguous arrays / structured buffers** as the core representation
  - **HDF5** or **Zarr** for offline snapshots
  - **Apache Arrow** if you need efficient handoff between systems/processes
  - **Shared memory / zero-copy buffers** if the renderer is separate but local

- **Rendering / deformation**
  - **Unity / Unreal** if you want an engine
  - **Three.js / Babylon.js** for web
  - **OpenGL/Vulkan** with **marching cubes** or **dual contouring** for extracting surfaces from scalar fields
  - **Compute shaders** to keep the field on GPU and avoid slow CPU-GPU transfers

1) **Best architecture for “not super slow”**

- Keep the field in a **GPU buffer**
- Update it in-place with **compute shaders/CUDA**
- Send only:
  - changed regions, or
  - compact snapshots, or
  - an ID + shared buffer handle
- Render from the same buffer or a copied GPU texture/buffer
- Use **chunking / tiling / sparse grids** if the plane is huge
- Use **double buffering** if another system needs a consistent frame while you keep updating

## Implementation Suggestions

For scientific, very high-volume data, I’d do this:

**Math/state**

- Represent the system as a **field** on a grid.
- Use **PDEs** if the dynamics are physical.
- Use **finite difference / finite volume** methods for the update rule.
- If the domain is huge, use a **sparse adaptive grid** or **domain decomposition**.
- If the field needs smooth geometry later, store it as a **scalar field** or **SDF**.

**Best stack**

- **Core simulation:** C++ or CUDA
- **GPU compute:** CUDA if NVIDIA-only, otherwise **Vulkan compute** or **OpenCL**
- **Python only for orchestration/analysis**, not the hot loop
- **Data format:** **Zarr** or **HDF5** for large chunked scientific arrays
- **Inter-process handoff:** **Apache Arrow**, shared memory, or ZeroMQ for streaming
- **Visualization/rendering:** a separate process in **Unity/Unreal** or a custom renderer using **marching cubes / dual contouring**

**Why this works**

- The simulation stays in **contiguous chunked arrays**
- Only active chunks update
- GPU does the heavy math
- Renderer reads from a separate buffer/process so simulation doesn’t stall

**Recommended architecture**

1. **Simulation engine** in C++/CUDA
2. Field stored as **chunked 3D arrays**
3. Update only dirty/active regions
4. Periodically emit **compressed snapshots** or **delta frames**
5. Renderer consumes those frames and builds 3D surfaces from the field

**Practical library choices**

- **C++:** Eigen, Kokkos, Thrust
- **CUDA:** raw CUDA kernels + cuBLAS/cuFFT if needed
- **Python:** NumPy, Dask, Zarr, Numba
- **Visualization:** VTK, Open3D, ParaView, or custom OpenGL/Vulkan
- **Distributed scale:** MPI + HDF5/Zarr + domain decomposition

**If you want the fastest realistic option**

- **C++ + CUDA + Zarr + MPI + Vulkan/OpenGL renderer**
- That’s the strongest combo for very large scientific fields.

## Reference Architecture

1. **Simulation core**
   - C++ for control and data layout
   - CUDA for heavy per-cell updates
   - Field stored as chunked 2D/3D arrays

2. **Domain decomposition**
   - Split the grid into tiles/chunks
   - Each chunk has its own update buffer
   - Neighbor exchange only at boundaries

3. **Update loop**
   - Read chunk state
   - Apply equation set
   - Write next state into a second buffer
   - Swap buffers each timestep

4. **Streaming / handoff**
   - Publish only changed chunks or frame deltas
   - Use shared memory if local
   - Use ZeroMQ or MPI if distributed
   - Use Arrow if you need efficient columnar transfer

5. **Persistence**
   - Save checkpoints in Zarr or HDF5
   - Compress chunks independently

6. **Rendering process**
   - Separate process/subsystem
   - Reads field snapshots or GPU buffer output
   - Converts scalar field to mesh with marching cubes or dual contouring
   - Deforms/render in 3D

7. **Scaling**
   - Use sparse grids or adaptive mesh refinement if the plane is huge
   - Keep active regions only where dynamics matter

## Recommended stacks

### 1) Python-only prototype

- **Math/update:** NumPy, SciPy, Numba
- **Large arrays:** Zarr, Dask
- **Streaming:** ZeroMQ or multiprocessing shared memory
- **Rendering:** VTK, PyVista, Open3D
- **Best for:** fast prototyping, smaller real-time demands

### 2) Mixed Python + C++

- **Core sim:** C++ or CUDA
- **Python:** orchestration, analysis, parameter sweeps
- **Storage:** HDF5 or Zarr
- **Interop:** pybind11
- **Rendering:** VTK or Unity/Unreal consuming streamed buffers
- **Best for:** scientific workflows with serious performance needs

### 3) C++-first / high-performance

- **Core sim:** C++17/20
- **GPU:** CUDA or Vulkan compute
- **Parallelism:** MPI + OpenMP
- **Data:** Zarr/HDF5
- **Render:** custom OpenGL/Vulkan, or ParaView/VTK for analysis
- **Best for:** maximum throughput and scale

## My recommendation

For your case, I’d choose:

- **Simulation:** C++ + CUDA
- **Parallel scaling:** MPI
- **Storage:** Zarr
- **Handoff:** shared memory or ZeroMQ
- **Rendering:** Vulkan/OpenGL or VTK/ParaView
- **Python:** analysis only

## High-level layout

[config/params]
[domain decomposition]
[simulation core]
[GPU kernels]
[streaming / handoff]
[storage / checkpoints]
[renderer interface]
[analysis tools]

```text
# Data model

FieldChunk:
  id
  bounds
  current_buffer
  next_buffer
  ghost_cells
  timestamp
  dirty_flag

FieldGrid:
  chunks[]
  neighbor_map
  active_region_index
```

```text
# Main loop

initialize_system()
load_initial_conditions()

while running:
  active_chunks = get_active_chunks()

  for each chunk in active_chunks:
    exchange_boundary_data(chunk)

  launch_gpu_update(active_chunks)

  for each chunk in active_chunks:
    swap_buffers(chunk)
    mark_dirty(chunk)

  if should_checkpoint():
    write_checkpoint(active_chunks)

  if should_stream_frame():
    publish_delta(active_chunks)

  if should_render():
    send_render_packet(active_chunks)
```

```text
# Update step

GPU_Update_Chunk(chunk):
  for each cell in chunk in parallel:
    neighborhood = read_local_stencil(cell)
    source_terms = evaluate_equations(cell, neighborhood, time)
    next_value = integrate(cell.value, source_terms, dt)
    write next_value to next_buffer
```

```text
# Boundary exchange

exchange_boundary_data(chunk):
  for each neighbor:
    send edge cells to neighbor
    receive neighbor edge cells
    write received data into ghost_cells
```

```text
# Chunk activation

get_active_chunks():
  active = []
  for chunk in all_chunks:
    if chunk has nontrivial dynamics:
      active.append(chunk)
  return active
```

```text
# Checkpointing

write_checkpoint(active_chunks):
  for each chunk:
    compress(chunk.current_buffer)
    save_to_zarr_or_hdf5(chunk.id, chunk.bounds, chunk.data, timestamp)
```

```text
# Streaming to renderer

publish_delta(active_chunks):
  packet = new FramePacket()
  for each chunk in active_chunks:
    if chunk.dirty_flag:
      packet.add(chunk.id, compressed_delta(chunk))
      chunk.dirty_flag = false
  send(packet)
```

```text
# Renderer side

on_receive(packet):
  for each chunk_update in packet:
    update_local_field_representation(chunk_update)

  if meshing_required():
    mesh = marching_cubes(local_field)
    render(mesh)
```

```text
# Adaptive refinement

refine_grid():
  for each chunk:
    if error_estimate(chunk) > threshold:
      split chunk into smaller chunks

coarsen_grid():
  for each group of child chunks:
    if variation is low:
      merge into parent chunk
```

```text
# Mixed-language split

Python:
  - parameter sweeps
  - experiment orchestration
  - offline analysis
  - plotting

C++/CUDA:
  - timestep updates
  - boundary exchange
  - chunk management
  - compression hooks

Renderer:
  - separate process
  - reads streamed field deltas
  - converts field to 3D geometry
```

```text
# Minimal module list

main_simulation
  init
  loop
  shutdown

field_storage
  chunk
  grid
  compression

numerics
  stencil_ops
  integrators
  boundary_conditions

gpu_backend
  kernels
  memory_management
  stream_sync

messaging
  packet_format
  sender
  receiver

render_bridge
  mesh_generation
  frame_sync
  scene_update
```

**Python orchestration + C++ compute split**.

```text
# Python orchestration + C++/CUDA compute split

# Python side responsibilities:
# - load config
# - start simulation worker
# - manage experiments
# - receive streamed frames
# - trigger checkpoints
# - forward data to renderer / analysis

# C++/CUDA side responsibilities:
# - own the field buffers
# - update chunks on GPU
# - exchange boundaries
# - emit deltas / snapshots
```

```text
# Python orchestrator

load_config()
sim = start_native_simulation(config)
renderer = start_renderer(config)

while running:
  command = check_ui_or_control_input()
  if command exists:
    sim.send(command)

  if sim.has_frame():
    frame = sim.recv_frame()
    renderer.send(frame)
    analyze_if_needed(frame)

  if sim.needs_checkpoint():
    sim.request_checkpoint()

  sleep_small_interval()
```

```text
# Python experiment runner

for parameter_set in parameter_sweep:
  sim = start_native_simulation(parameter_set)

  for t in range(num_steps):
    sim.step()
    if t % checkpoint_interval == 0:
      sim.request_checkpoint()
    if t % render_interval == 0:
      frame = sim.recv_frame()
      save_preview(frame)

  results = sim.finalize()
  save_results(results)
```

```text
# Python <-> native interface

start_native_simulation(config):
  launch native process or load shared library
  pass config
  return simulation_handle

simulation_handle.step():
  send "advance_one_step"

simulation_handle.recv_frame():
  receive compressed chunk deltas

simulation_handle.request_checkpoint():
  send "save_current_state"

simulation_handle.send(command):
  forward control message to native side
```

```text
# Native simulation process

main():
  config = read_config()
  grid = initialize_grid(config)
  gpu = init_gpu(config)
  comm = init_messaging(config)

  while running:
    msg = poll_control_messages()

    if msg == "advance_one_step":
      active_chunks = select_active_chunks(grid)
      exchange_boundaries(active_chunks, comm)
      launch_gpu_update(active_chunks, gpu)
      collect_changed_chunks(active_chunks)
      maybe_stream_frame(active_chunks, comm)

    if msg == "save_current_state":
      write_checkpoint(grid)

    if msg == "shutdown":
      running = false
```

```text
# Native data layout

struct Chunk {
  id
  bounds
  device_buffer_current
  device_buffer_next
  host_staging_buffer
  ghost_cells
  dirty_flag
  refinement_level
}

struct Grid {
  chunks[]
  neighbor_map
  active_chunk_list
}
```

```text
# GPU update path

launch_gpu_update(active_chunks, gpu):
  for each chunk in active_chunks:
    upload any needed control parameters
    run kernel_update_chunk(chunk)

kernel_update_chunk(chunk):
  for each cell in chunk in parallel:
    stencil = load_neighbor_values(cell, ghost_cells)
    rhs = evaluate_equations(cell.state, stencil, time)
    next_state = integrate(cell.state, rhs, dt)
    write next_state to device_buffer_next
```

```text
# Boundary exchange path

exchange_boundaries(active_chunks, comm):
  for each chunk:
    pack edge data into send buffer
    send to neighbor process or thread
    receive neighbor boundary data
    unpack into ghost_cells
```

```text
# Delta streaming path

maybe_stream_frame(active_chunks, comm):
  frame = new FramePacket()

  for each chunk in active_chunks:
    if chunk.dirty_flag:
      delta = compress_delta(chunk.device_buffer_current)
      frame.add(chunk.id, chunk.bounds, delta)
      chunk.dirty_flag = false

  if frame not empty:
    comm.send(frame)
```

```text
# Checkpoint path

write_checkpoint(grid):
  for each chunk in grid.chunks:
    snapshot = copy_chunk_to_host(chunk.device_buffer_current)
    compressed = compress(snapshot)
    save_to_zarr_or_hdf5(chunk.id, compressed, chunk.bounds)
```

```text
# Renderer side

on_frame_received(frame):
  for each update in frame:
    update_local_field_buffer(update)

  if enough_updates_accumulated():
    mesh = generate_mesh_from_field(local_field_buffer)
    render(mesh)
```

```text
# Suggested boundary between Python and native code

Python owns:
  - experiment definitions
  - parameter sweeps
  - logging
  - result analysis
  - visualization control

Native owns:
  - all field memory
  - all numerical kernels
  - all chunk updates
  - all high-rate messaging
```

```text
# Practical call pattern

Python:
  sim = launch_sim(config)
  sim.set_parameters(params)
  sim.step()
  frame = sim.get_latest_frame()
  sim.save_checkpoint()

Native:
  runs continuous loop
  responds to control messages
  pushes frames asynchronously
```

```text
# Best-praxis note in pseudocode form

if performance matters:
  do not move full field through Python each step
  do not copy GPU -> CPU unless needed
  do not mesh on the simulation thread
  keep renderer decoupled
  prefer chunked updates over full-frame transfers
```

 **file-by-file project skeleton**

```text
project/
  python/
    orchestrator.py
    experiment_runner.py
    renderer_bridge.py
    analysis.py
    config.py
    bindings.py

  native/
    CMakeLists.txt
    main.cpp
    simulation/
      grid.hpp
      grid.cpp
      chunk.hpp
      chunk.cpp
      timestep.hpp
      timestep.cpp
      boundaries.hpp
      boundaries.cpp
      compression.hpp
      compression.cpp
    gpu/
      kernels.cu
      kernels.hpp
      memory.cu
      memory.hpp
    comm/
      ipc.hpp
      ipc.cpp
      zmq_bridge.hpp
      zmq_bridge.cpp
    io/
      checkpoint.hpp
      checkpoint.cpp
      zarr_writer.cpp
      hdf5_writer.cpp
    render/
      frame_packet.hpp
      frame_packet.cpp
      mesh_extract.hpp
      mesh_extract.cpp
```

```text
# python/config.py

load_config(path):
  read JSON/YAML
  return sim_params
```

```text
# python/orchestrator.py

main():
  config = load_config("config.yaml")
  sim = launch_native_process(config)
  renderer = launch_renderer(config)

  while running:
    if sim.has_message():
      msg = sim.receive()
      renderer.forward(msg)

    if user_requested_step():
      sim.send("advance")

    if user_requested_checkpoint():
      sim.send("checkpoint")

    if user_requested_stop():
      sim.send("shutdown")
      break
```

```text
# python/experiment_runner.py

run_sweep(parameter_sets):
  for params in parameter_sets:
    sim = launch_native_process(params)

    for step in range(params.steps):
      sim.send("advance")

      if step % params.render_interval == 0:
        frame = sim.receive_frame()
        save_preview(frame)

      if step % params.checkpoint_interval == 0:
        sim.send("checkpoint")

    collect_final_outputs(sim)
```

```text
# python/renderer_bridge.py

send_to_renderer(frame_packet):
  serialize frame_packet
  write to socket or shared memory
```

```text
# python/bindings.py

# optional, if using pybind11
load_native_module():
  expose:
    - create_simulation()
    - step()
    - set_parameters()
    - get_frame()
    - save_checkpoint()
    - shutdown()
```

```text
# native/main.cpp

int main():
  config = read_config()
  grid = initialize_grid(config)
  gpu = initialize_gpu(config)
  comm = initialize_comm(config)

  while running:
    msg = comm.poll()

    if msg == ADVANCE:
      step_simulation(grid, gpu, comm)

    if msg == CHECKPOINT:
      write_checkpoint(grid)

    if msg == SHUTDOWN:
      running = false
```

```text
# native/simulation/grid.hpp

struct Grid:
  vector<Chunk> chunks
  neighbor_map
  active_chunk_ids
```

```text
# native/simulation/chunk.hpp

struct Chunk:
  id
  bounds
  current_device_buffer
  next_device_buffer
  host_staging_buffer
  ghost_cells
  dirty_flag
```

```text
# native/simulation/timestep.cpp

step_simulation(grid, gpu, comm):
  active = select_active_chunks(grid)
  exchange_boundaries(active, comm)
  launch_gpu_kernels(active, gpu)
  swap_buffers(active)
  package_deltas(active, comm)
```

```text
# native/simulation/boundaries.cpp

exchange_boundaries(active, comm):
  for chunk in active:
    pack_edges(chunk)
    send_to_neighbors(chunk)
    receive_neighbor_edges(chunk)
    unpack_into_ghost_cells(chunk)
```

```text
# native/gpu/kernels.cu

kernel_update_chunk(chunk):
  for each cell in chunk in parallel:
    neighbors = read_stencil(cell)
    rhs = compute_rhs(cell.state, neighbors)
    next_state = integrate(cell.state, rhs, dt)
    write next_state to next_buffer
```

```text
# native/gpu/memory.cu

initialize_device_buffers(grid):
  for chunk in grid.chunks:
    allocate current and next buffers on GPU
    allocate staging buffers if needed
```

```text
# native/comm/ipc.cpp

package_and_send(frame):
  compress_dirty_chunks(frame)
  send via shared memory or socket
```

```text
# native/io/checkpoint.cpp

write_checkpoint(grid):
  for chunk in grid.chunks:
    copy_device_to_host(chunk)
    compress(chunk)
    save_chunk_to_disk(chunk)
```

```text
# native/render/mesh_extract.cpp

build_render_packet(grid):
  field = gather_visible_chunks(grid)
  mesh = marching_cubes(field)
  serialize(mesh)
  return mesh_packet
```

```text
# build flow

cmake_configure_native()
build_cuda_kernels()
build_python_bindings_if_needed()
run_python_orchestrator()
```

```text
# runtime flow

python -> native:
  start
  config
  advance
  checkpoint
  shutdown

native -> python:
  progress
  frame deltas
  checkpoint complete
  errors

native -> renderer:
  mesh packets
  field deltas
```
