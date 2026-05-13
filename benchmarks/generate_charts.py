import matplotlib.pyplot as plt

methods = ['Brute Force\nO(n)', 'Lurox\nHash Index O(1)']
latencies = [220, 2]
colors = ['#ff6b6b', '#00ff88']

fig, ax = plt.subplots(figsize=(8, 5), facecolor='#0a0a1a')
ax.set_facecolor('#0a0a1a')

bars = ax.bar(methods, latencies, color=colors, edgecolor='white', linewidth=1.5)

for bar, val in zip(bars, latencies):
    ax.text(bar.get_x() + bar.get_width()/2, val + 8,
            f'{val}ms', ha='center', color='white', fontsize=14, fontweight='bold')

ax.set_ylabel('Query Latency (ms)', color='white', fontsize=12)
ax.set_title('Lurox Query Speedup', color='#00ff88', fontsize=16, fontweight='bold', pad=20)
ax.tick_params(colors='white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('white')
ax.spines['bottom'].set_color('white')

plt.tight_layout()
plt.savefig('benchmarks/lurox_speedup.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')