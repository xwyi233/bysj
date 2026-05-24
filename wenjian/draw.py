import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 设置中文字体，防止乱码 (若在Mac上请改为 'Arial Unicode MS')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建 1x2 的画布
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ==========================================
# 图 (a): 天窗双向封锁约束图解
# ==========================================
ax1.set_title("(a) 天窗双向封锁约束图解", fontsize=14, pad=15)
ax1.set_yticks([0, 1])
ax1.set_yticklabels(['车站 B\n(区间终点)', '车站 A\n(区间起点)'], fontsize=12)
ax1.set_xlabel('时间 (分钟)', fontsize=12)
ax1.set_ylim(-0.2, 1.2)
ax1.set_xlim(0, 450)
ax1.grid(axis='x', linestyle=':', alpha=0.6)

# 绘制天窗影响区
window_start, window_length = 100, 100
window = patches.Rectangle((window_start, 0), window_length, 1,
                           facecolor='dimgray', alpha=0.6, label='天窗影响区 (绝对封锁)')
ax1.add_patch(window)

# 绘制天窗前 15min 安全冗余区
pre_margin_start = window_start - 15
pre_margin_length = 15
pre_margin = patches.Rectangle((pre_margin_start, 0), pre_margin_length, 1,
                              facecolor='lightgray', alpha=0.5, hatch='\\\\', label='15min 安全冗余 (物理留白)')
ax1.add_patch(pre_margin)

# 绘制天窗后 15min 安全冗余区
post_margin_start = window_start + window_length
post_margin_length = 15
post_margin = patches.Rectangle((post_margin_start, 0), post_margin_length, 1,
                                facecolor='lightgray', alpha=0.5, hatch='\\\\')
ax1.add_patch(post_margin)

# 绘制列车运行线
# 1. 冗余区前的合法列车
ax1.plot([30, 65], [1, 0], 'g-', lw=2.5, label='合法运行线')
ax1.text(25, 1.05, '$x_{1,q}$', color='green', fontsize=12)
ax1.text(60, -0.1, '$y_{1,q}$', color='green', fontsize=12)

# 2. 侵入前冗余区的非法列车
ax1.plot([75, 110], [1, 0], 'r--', lw=2.5, label='非法运行线 (冲突)')
ax1.plot(92.5, 0.5, 'rx', markersize=12, markeredgewidth=2)  # 冲突标记

# 3. 穿越天窗的非法列车
ax1.plot([130, 180], [1, 0], 'r--', lw=2.5)
ax1.plot(155, 0.5, 'rx', markersize=12, markeredgewidth=2)

# 4. 侵入后冗余区的非法列车
ax1.plot([230, 280], [1, 0], 'r--', lw=2.5)
ax1.plot(255, 0.5, 'rx', markersize=12, markeredgewidth=2)

# 5. 天窗及冗余后的合法列车
ax1.plot([350, 400], [1, 0], 'b-', lw=2.5, label='合法运行线 (冗余后)')
ax1.text(345, 1.05, '$x_{i,q}$', color='blue', fontsize=12)
ax1.text(395, -0.1, '$y_{i,q}$', color='blue', fontsize=12)

ax1.legend(loc='lower left', fontsize=10)

# ==========================================
# 图 (b): 区间防越行限制图解
# ==========================================
ax2.set_title("(b) 区间防越行限制图解", fontsize=14, pad=15)
ax2.set_yticks([0, 1])
ax2.set_yticklabels(['车站 B\n(区间终点)', '车站 A\n(区间起点)'], fontsize=12)
ax2.set_xlabel('时间 (分钟)', fontsize=12)
ax2.set_ylim(-0.2, 1.2)
ax2.set_xlim(0, 200)
ax2.grid(axis='x', linestyle=':', alpha=0.6)

# 1. 先发列车 i (慢速)
ax2.plot([30, 140], [1, 0], 'gray', lw=2.5, label='先发列车 $i$ (慢速)')
ax2.text(25, 1.05, '$x_{i,q}$', color='gray', fontsize=12)
ax2.text(135, -0.1, '$y_{i,q}$', color='gray', fontsize=12)

# 2. 后发列车 j (快速 - 导致非法越行)
ax2.plot([60, 100], [1, 0], 'r--', lw=2.5, label='未调整列车 $i+1$ (非法越行)')
ax2.text(55, 1.05, '$x_{i+1,q}$', color='red', fontsize=12)
ax2.text(95, -0.1, '$y_{i+1,q}$', color='red', fontsize=12)
# 标记越行冲突点
ax2.plot(78.5, 0.56, 'rx', markersize=12, markeredgewidth=2)

# 3. 调整后的列车 j (在车站 A 待避)
# 增加前置车站等待时间 w_{j, q-1}
ax2.plot([60, 145], [1, 1], 'b-.', lw=2, label='前置车站待避时间 $w_{i, s}$')
ax2.plot([145, 185], [1, 0], 'b-', lw=2.5, label='调整后列车 $i+1$ (合法尾随)')
ax2.text(140, 1.05, "$x'_{i+1,q}$", color='blue', fontsize=12)
ax2.text(180, -0.1, "$y'_{i+1,q}$", color='blue', fontsize=12)

ax2.legend(loc='lower left', fontsize=10)

# 调整布局并保存/显示
plt.tight_layout()
plt.savefig('constraint_diagrams.png', dpi=300, bbox_inches='tight')
plt.show()