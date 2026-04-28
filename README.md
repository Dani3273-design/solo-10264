# 井字棋游戏

一个基于 Pygame 的井字棋游戏，支持双人对战。

## 环境要求

- Python 3.9+
- Pygame

## 目录结构

```
main/
├── main.py          # 游戏入口文件
├── pk/
│   └── tic_tac_toe.py  # 游戏核心逻辑
└── README.md        # 本说明文件
```

## 安装依赖

```bash
pip install pygame
```

## 运行游戏

```bash
cd main
python main.py
```

## 游戏规则

1. **玩家**：红圈(O)和黑叉(X)双方对战
2. **先手**：红圈(O)先下
3. **限时**：每步限时10秒，超时判负
4. **获胜条件**：横、竖、斜向连成三个同色棋子
5. **平局**：棋盘下满无人获胜即平局
6. **认输**：游戏中可点击右下角"认输"按钮直接判负

## 功能特性

### 1. 美观的UI界面
- 整洁的井字棋盘布局
- 清晰的按钮设计
- 游戏状态信息展示

### 2. 实时倒计时
- 顶部显示当前玩家信息
- 中央显示10秒倒计时
- 剩余3秒时倒计时文字变红警告

### 3. 多线程胜负判断
- 每步棋后，胜负判断在独立线程中执行
- 不阻塞主线程，保证操作流畅不卡顿
- 检测到获胜时自动高亮显示获胜连线

### 4. 音效系统
- 下棋音效
- 获胜音效
- 失败音效
- 平局音效

### 5. 中文支持
- 自动检测并加载系统中的中文字体
- 支持 macOS 系统字体：PingFang、STHeiti、Hiragino Sans GB、SimHei

## 代码解析

### 核心类：TicTacToeGame

**主要方法说明：**

- `__init__()`: 初始化游戏，包括 Pygame、音效、字体和游戏状态
- `_init_sounds()`: 生成音效（使用正弦波生成简单音效）
- `_init_fonts()`: 自动搜索并加载系统中文字体
- `_init_game_state()`: 初始化游戏状态（棋盘、当前玩家、计时器等）

- `_start_win_check(player)`: 启动多线程胜负检测
  - 创建棋盘副本
  - 启动独立线程进行胜负判断
  - 不阻塞主线程

- `_win_check_worker(board, player)`: 胜负检测线程工作函数
  - 检查8种获胜模式（3行+3列+2对角线）
  - 检查棋盘是否填满（平局）
  - 使用锁机制防止并发冲突

- `_make_move(row, col)`: 处理落子逻辑
  - 更新棋盘状态
  - 播放落子音效
  - 启动胜负检测线程
  - 切换玩家，重置计时器

- `_draw_board()`: 绘制棋盘和棋子
  - 绘制4条分隔线
  - 根据棋盘状态绘制圆圈或叉
  - 获胜时高亮显示获胜连线

- `run()`: 游戏主循环
  - 处理用户输入事件
  - 根据游戏状态渲染不同界面
  - 控制帧率（60FPS）

### 游戏状态机

```
start (开始界面)
    ↓ 点击"开始游戏"
playing (游戏中)
    ↓ 获胜/平局/超时/认输
game_over (游戏结束)
    ↓ 点击"重新开始" → playing
    ↓ 点击"返回主菜单" → start
```

## 关键技术点

### 1. 多线程胜负判断
```python
def _start_win_check(self, player):
    board_copy = [row.copy() for row in self.board]
    
    self.win_thread = threading.Thread(
        target=self._win_check_worker,
        args=(board_copy, player),
        daemon=True
    )
    self.win_thread.start()
```
- 使用线程副本避免数据竞争
- daemon=True 确保主线程退出时子线程自动结束
- 使用锁机制保护共享状态修改

### 2. 中文支持
```python
font_paths = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/SimHei.ttf",
]
```
- 遍历常见 macOS 中文字体路径
- 自动使用第一个可用字体
- 失败时回退到系统默认字体

### 3. 动态生成音效
```python
def _generate_sound(self, frequency, duration):
    # 使用正弦波生成简单音效
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = float(i) / sample_rate
        buf[i] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
    return pygame.mixer.Sound(buffer=buf)
```
- 无需外部音频文件
- 根据频率生成不同音调
- 可自定义音量和时长

## 已知问题

1. 如果系统中没有中文字体，中文可能显示为方框
2. 音效使用正弦波生成，比较简单
3. 仅支持本地双人对战，不支持AI或网络对战

## 开发计划（可选）

- 添加AI对手
- 支持网络对战
- 添加游戏记录功能
- 自定义主题颜色
- 支持自定义棋盘大小

## License

MIT License
