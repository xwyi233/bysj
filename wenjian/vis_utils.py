"""
Visualization Utilities for JSP
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib as mpl

try:
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
    mpl.rcParams['axes.unicode_minus'] = False
except:
    pass

def get_station_name(i):
    """动态获取车站名，如 0->A, 1->B ... 26->S26"""
    if i < 26:
        return chr(65 + i)
    return f'S{i}'

def wrap_trajectory(times, positions, cycle=24*60):
    """
    处理时间跨越周期的辅助函数。
    将跨越 cycle (如1440) 的线段拆分成到达边缘和从 0 重新开始的两段。
    """
    w_times = []
    w_positions = []

    for i in range(len(times)):
        if i == 0:
            if pd.isna(times[i]):
                w_times.append(np.nan)
                w_positions.append(np.nan)
            else:
                w_times.append(times[i] % cycle)
                w_positions.append(positions[i])
            continue

        t_prev = times[i-1]
        p_prev = positions[i-1]
        t_curr = times[i]
        p_curr = positions[i]

        if pd.isna(t_prev) or pd.isna(t_curr):
            if not pd.isna(t_curr):
                w_times.append(t_curr % cycle)
                w_positions.append(p_curr)
            else:
                w_times.append(np.nan)
                w_positions.append(np.nan)
            continue

        if t_prev > t_curr: # 数据异常防御
            w_times.append(t_curr % cycle)
            w_positions.append(p_curr)
            continue

        cycle_prev = int(t_prev // cycle)
        cycle_curr = int(t_curr // cycle)

        if cycle_prev == cycle_curr:
            w_times.append(t_curr % cycle)
            w_positions.append(p_curr)
        else:
            # 跨越了一个或多个24h周期
            c = cycle_prev
            while c < cycle_curr:
                t_bound = (c + 1) * cycle
                if t_curr == t_prev:
                    p_bound = p_prev
                else:
                    p_bound = p_prev + (p_curr - p_prev) * ((t_bound - t_prev) / (t_curr - t_prev))

                w_times.append(cycle)  # 画到右边缘 (1440)
                w_positions.append(p_bound)

                w_times.append(np.nan) # 打断连线
                w_positions.append(np.nan)

                w_times.append(0)      # 从左边缘 (0) 重新开始
                w_positions.append(p_bound)

                c += 1

            w_times.append(t_curr % cycle)
            w_positions.append(p_curr)

    return w_times, w_positions


def plot_train_graph(schedule, n_machines, n_jobs, save_path, train_names_dict=None, maintenance_job_ids=None):
    """
    绘制高铁运行图 (Time-Distance Graph) - 24h 循环周期
    """
    if train_names_dict is None: train_names_dict = {}
    if maintenance_job_ids is None: maintenance_job_ids = []

    plt.figure(figsize=(15, 8))

    n_sections = n_machines // 2
    n_stations = n_sections + 1

    # 动态生成颜色
    colors = plt.cm.tab20(np.linspace(0, 1, max(20, n_jobs)))

    # 动态建立机器(Machine)到物理位置(Position)的映射
    machine_positions = {}
    for m in range(n_sections):
        machine_positions[m] = (m, m + 1)            # 下行
        opp_m = n_machines - 1 - m
        machine_positions[opp_m] = (m + 1, m)        # 上行

    for job_id in range(n_jobs):
        job_ops = []
        for (j, op), (m, start, end) in schedule.items():
            if j == job_id:
                job_ops.append((op, m, start, end))

        if not job_ops:
            continue

        job_ops.sort(key=lambda x: x[0])
        times = []
        positions = []

        last_p_end = None # 记录上一次操作结束的位置

        for op, m, start, end in job_ops:
            if m not in machine_positions:
                continue
            p_start, p_end = machine_positions[m]

            # S站的索引为18，O站的索引为14
            O_idx = 14
            S_idx = 18

            # 如果上一个操作结束点到当前起点的跳跃发生在S和O之间，插入 nan 断开连线
            if last_p_end is not None:
                is_SO_jump = (last_p_end == O_idx and p_start == S_idx) or (last_p_end == S_idx and p_start == O_idx)
                if is_SO_jump:
                    times.extend([np.nan, np.nan])
                    positions.extend([np.nan, np.nan])

            # 如果操作本身就在S和O之间，则隐藏这段运行线
            is_SO_op = (p_start == O_idx and p_end == S_idx) or (p_start == S_idx and p_end == O_idx)
            if is_SO_op:
                times.extend([np.nan, np.nan])
                positions.extend([np.nan, np.nan])
            else:
                # 记录起点时间和位置
                times.append(start)
                positions.append(p_start)
                # 记录终点时间和位置
                times.append(end)
                positions.append(p_end)

            last_p_end = p_end

        # 动态获取真实车次名称
        actual_train_name = train_names_dict.get(job_id, f'T{job_id + 1}')

        # 天窗列车样式
        if job_id in maintenance_job_ids:
            label_added = False
            for i in range(0, len(times), 2):
                t_start = times[i]
                t_end = times[i + 1]
                p_start = positions[i]
                p_end = positions[i + 1]

                if pd.isna(t_start) or pd.isna(t_end):
                    continue

                # 应用截断逻辑处理跨天数据
                w_t, w_p = wrap_trajectory([t_start, t_end], [p_start, p_end])

                label_str = f'Skylight ({actual_train_name})' if not label_added else ""
                plt.plot(w_t, w_p, '-', color='gray', linewidth=10, alpha=0.3, label=label_str)
                plt.plot(w_t, w_p, '--', color='black', linewidth=1)
                label_added = True
        else:
            # 普通列车
            # 应用截断逻辑处理跨天数据
            w_times, w_positions = wrap_trajectory(times, positions)

            # 单独提取原始的包装后节点时间，用于画圆点，避免在线段边缘画无关圆点
            orig_w_times = [t % (24*60) if not pd.isna(t) else np.nan for t in times]

            c = colors[job_id % len(colors)]
            plt.plot(w_times, w_positions, '-', label=actual_train_name, color=c, linewidth=2)
            plt.plot(orig_w_times, positions, 'o', color=c, markersize=4) # 绘制车站经停点

            if times:
                # 找到第一个非 nan 的坐标点来放置文本标签
                first_valid_idx = next((i for i, t in enumerate(orig_w_times) if not pd.isna(t)), -1)
                if first_valid_idx != -1:
                    plt.text(orig_w_times[first_valid_idx], positions[first_valid_idx], actual_train_name,
                             verticalalignment='bottom', fontsize=9, fontweight='bold')

    # X轴刻度：严格限制在 0h 到 24h
    ticks = np.arange(0, 25 * 60, 60)
    tick_labels = [f'{int(t // 60)}h' for t in ticks]
    plt.xticks(ticks, tick_labels, rotation=45)
    plt.xlim(0, 24 * 60)

    plt.xlabel('Time (Hours)', fontsize=14)
    plt.ylabel('Station', fontsize=14)
    plt.title('High-Speed Railway Train Graph (运行图 - 24h Cycle)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Y轴刻度：动态生成车站名称 A, B, C...
    station_names = [get_station_name(i) for i in range(n_stations)]
    plt.yticks(range(n_stations), station_names)

    # 将图例放在外面防止遮挡
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_gantt_chart(schedule, n_machines, n_jobs, save_path, train_names_dict=None):
    """
    绘制资源占用甘特图 - 24h 循环周期
    """
    if train_names_dict is None: train_names_dict = {}

    plt.figure(figsize=(15, 8))
    colors = plt.cm.tab20(np.linspace(0, 1, max(20, n_jobs)))

    n_sections = n_machines // 2
    n_stations = n_sections + 1

    station_names = [get_station_name(i) for i in range(n_stations)]

    # 动态显式标明各个机器代表的区间
    machine_names = {}
    for m in range(n_sections):
        machine_names[m] = f'M{m} ({station_names[m]}->{station_names[m+1]})'
        opp_m = n_machines - 1 - m
        machine_names[opp_m] = f'M{opp_m} ({station_names[m+1]}->{station_names[m]})'

    cycle = 24 * 60  # 1440 mins

    for (job_id, op_idx), (machine_id, start, end) in schedule.items():
        duration = end - start
        actual_train_name = train_names_dict.get(job_id, f'T{job_id + 1}')
        c = colors[job_id % len(colors)]

        # 判断是否跨越 24h 周期边界，跨越则切片展示
        start_cycle = int(start // cycle)
        end_cycle = int(end // cycle)

        if start_cycle == end_cycle:
            w_start = start % cycle
            plt.barh(machine_id, duration, left=w_start, height=0.6, color=c, edgecolor='black', alpha=0.8)
            if duration > 2:
                plt.text(w_start + duration / 2, machine_id, actual_train_name, ha='center', va='center', color='white', fontsize=8)
        else:
            current_c = start_cycle
            curr_start = start
            while current_c < end_cycle:
                t_bound = (current_c + 1) * cycle
                dur = t_bound - curr_start
                w_start = curr_start % cycle
                plt.barh(machine_id, dur, left=w_start, height=0.6, color=c, edgecolor='black', alpha=0.8)
                if dur > 2:
                    plt.text(w_start + dur / 2, machine_id, actual_train_name, ha='center', va='center', color='white', fontsize=8)
                curr_start = t_bound
                current_c += 1

            # 画最后一段
            dur = end - curr_start
            if dur > 0:
                w_start = curr_start % cycle
                plt.barh(machine_id, dur, left=w_start, height=0.6, color=c, edgecolor='black', alpha=0.8)
                if dur > 2:
                    plt.text(w_start + dur / 2, machine_id, actual_train_name, ha='center', va='center', color='white', fontsize=8)

    # 锁定 X 轴为 0-24h
    ticks = np.arange(0, 25 * 60, 60)
    tick_labels = [f'{int(t // 60)}h' for t in ticks]
    plt.xticks(ticks, tick_labels, rotation=45)
    plt.xlim(0, 24 * 60)

    plt.xlabel('Time (Hours)', fontsize=14)
    plt.ylabel('Resource (Station / Section)', fontsize=14)
    plt.title('Resource Occupation Gantt Chart (24h Cycle)', fontsize=16)

    plt.yticks(range(n_machines), [machine_names.get(i, f'M{i}') for i in range(n_machines)])
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def save_schedule_to_csv(schedule, save_path, train_names_dict=None):
    """
    将调度结果保存为CSV，并增加HH:MM的时间格式
    """
    if train_names_dict is None: train_names_dict = {}

    if not schedule:
        pd.DataFrame().to_csv(save_path, index=False)
        return

    n_machines = max([m_id for (_, _), (m_id, _, _) in schedule.items()]) + 1
    n_sections = n_machines // 2
    n_stations = n_sections + 1
    station_names = [get_station_name(i) for i in range(n_stations)]

    machine_names = {}
    for m in range(n_sections):
        machine_names[m] = f'M{m} ({station_names[m]}->{station_names[m+1]})'
        opp_m = n_machines - 1 - m
        machine_names[opp_m] = f'M{opp_m} ({station_names[m+1]}->{station_names[m]})'

    # 分钟转 小时:分钟 格式工具函数 (由于是日志报表，在此保留真实绝对时间，不断开)
    def format_time(mins):
        h = int(mins) // 60
        m = int(mins) % 60
        return f"{h}:{m:02d}"

    data = []
    for (job_id, op_idx), (machine_id, start, end) in schedule.items():
        actual_train_name = train_names_dict.get(job_id, f'T{job_id + 1}')
        data.append({
            'Job ID': job_id,  # 隐藏列，用于最后正确排序
            'Train ID': actual_train_name,
            'Operation ID': op_idx,
            'Station/Section (Machine)': machine_names.get(machine_id, f'M{machine_id}'),
            'Start Time (min)': start,
            'End Time (min)': end,
            'Start Time (HH:MM)': format_time(start),
            'End Time (HH:MM)': format_time(end),
            'Duration (min)': end - start
        })

    # 创建DataFrame
    df = pd.DataFrame(data)

    df = df.sort_values(by=['Job ID', 'Start Time (min)']).drop('Job ID', axis=1)

    # 保存为CSV
    df.to_csv(save_path, index=False, encoding='utf_8_sig')