import pygame
import random
import time


# Pygameの初期化
pygame.init()

# セルのサイズ
CELL_SIZE = 20
BLOCK_SIZE = CELL_SIZE  # セルサイズとブロックサイズを同じにする


# ゲームエリアの設定
GAME_AREA_WIDTH, GAME_AREA_HEIGHT = 12, 27  # セル単位
GAME_AREA_PIXEL_WIDTH = GAME_AREA_WIDTH * CELL_SIZE  # ピクセル単位
GAME_AREA_PIXEL_HEIGHT = GAME_AREA_HEIGHT * CELL_SIZE

# タイマーオブジェクトの作成
clock = pygame.time.Clock()

# スコアエリアの設定
SCORE_AREA_WIDTH = 200  # ピクセル単位

# ゲームエリアの左上の座標
GAME_AREA_X = 0
GAME_AREA_Y = 0


# 画面の全体的なサイズ
SCREEN_WIDTH = GAME_AREA_PIXEL_WIDTH + SCORE_AREA_WIDTH
SCREEN_HEIGHT = GAME_AREA_PIXEL_HEIGHT

# 画面のセットアップ
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# カラー設定
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),   # 赤
    (0, 255, 0),   # 緑
    (0, 0, 255),   # 青
    (255, 255, 0), # 黄
    (255, 165, 0), # オレンジ
    (128, 0, 128), # 紫
    (0, 255, 255)  # シアン
]

# テトロミノの形状
tetromino_shapes = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

# 次のブロック、タイマー、スコアを表示する関数
def draw_ui(surface, next_block, elapsed_time, score, lines_cleared):
    # UIエリアの設定
    ui_area_x = GAME_AREA_PIXEL_WIDTH + 10
    ui_area_y = 10
    next_block_text_y_offset = 20
    timer_text_y_offset = 100
    score_text_y_offset = 160
    lines_cleared_text_y_offset = 200

    # フォント設定
    font = pygame.font.SysFont(None, 24)

    # 次のブロックのタイトル
    next_block_text = font.render("Next Block", True, (0, 0, 0))
    surface.blit(next_block_text, (ui_area_x, ui_area_y))

    # 次のブロックの表示
    draw_next_block(next_block, surface, ui_area_x, ui_area_y + next_block_text_y_offset)

    # タイマーの表示
    time_text = font.render(f"Time: {int(elapsed_time)}s", True, (0, 0, 0))
    surface.blit(time_text, (ui_area_x, ui_area_y + timer_text_y_offset))

    # スコアの表示
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    surface.blit(score_text, (ui_area_x, ui_area_y + score_text_y_offset))

    # ライン消去数の表示
    lines_cleared_text = font.render(f"Lines: {lines_cleared}", True, (0, 0, 0))
    surface.blit(lines_cleared_text, (ui_area_x, ui_area_y + lines_cleared_text_y_offset))

def draw_next_block(block, surface, x, y):
    # 次のブロックのサイズに合わせたオフセットを計算
    block_width = max([len(row) for row in block.shape]) * CELL_SIZE
    block_height = len(block.shape) * CELL_SIZE
    offset_x = (SCORE_AREA_WIDTH - block_width) // 2
    offset_y = 30  # 適切なオフセットを設定

    # 次のブロックを描画
    for i, row in enumerate(block.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    surface,
                    block.color,
                    (x + offset_x + j * CELL_SIZE, y + offset_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

def fix_block_to_area(block, game_area):
    for y, row in enumerate(block.shape):
        for x, cell in enumerate(row):
            if cell:
                game_area[block.y + y][block.x + x] = block.color

def check_and_clear_lines(game_area):
    lines_cleared = 0  # 消去したライン数
    for y, row in enumerate(game_area):
        if all(row):
            del game_area[y]
            game_area.insert(0, [0] * GAME_AREA_WIDTH)
            lines_cleared += 1

    if lines_cleared > 0:
        scores = {1: 40, 2: 100, 3: 300, 4: 1200}
        Block.score += scores.get(lines_cleared, 0)
        Block.lines_cleared += lines_cleared  # 消去したライン数を更新

    return lines_cleared
def check_and_clear_lines(game_area):
    lines_cleared = 0  # 消去したライン数
    for y, row in enumerate(game_area):
        if all(row):
            del game_area[y]
            game_area.insert(0, [0] * GAME_AREA_WIDTH)
            lines_cleared += 1

    if lines_cleared > 0:
        scores = {1: 40, 2: 100, 3: 300, 4: 1200}
        Block.score += scores.get(lines_cleared, 0)
        Block.lines_cleared += lines_cleared
        print(f"Lines cleared: {Block.lines_cleared}")  # ここで消去したライン数を出力

    return lines_cleared


# ゲームエリアの囲いを描画する関数
def draw_game_area_border(surface, area_x, area_y, area_width, area_height, border_color, border_thickness):
    pygame.draw.rect(surface, border_color, (area_x - border_thickness, area_y - border_thickness,
                                             area_width + border_thickness * 2, area_height + border_thickness * 2),
                                             border_thickness)

# ゴーストブロック（落下予測）を描画する関数
def draw_ghost_block(surface, block, game_area):
    # ブロックの現在の位置をコピー
    ghost_x, ghost_y = block.x, block.y
    # ブロックが衝突するまで下に移動
    while block.is_valid_position(game_area, new_x=ghost_x, new_y=ghost_y + 1):
        ghost_y += 1
    # ゴーストブロックを半透明で描画
    for y, row in enumerate(block.shape):
        for x, cell in enumerate(row):
            if cell:
                rect_x = GAME_AREA_X + (ghost_x + x) * BLOCK_SIZE
                rect_y = GAME_AREA_Y + (ghost_y + y) * BLOCK_SIZE
                ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                ghost_surface.set_alpha(128)  # 半透明のアルファ値を設定
                ghost_surface.fill(block.color)  # ゴーストブロックの色を塗りつぶす
                surface.blit(ghost_surface, (rect_x, rect_y))

def check_game_over(game_area):
    """ゲームオーバーをチェックする関数"""
    return any(game_area[0])



# ブロッククラス
class Block:
    # ブロックの初期化
    score = 0  # クラス変数として定義
    lines_cleared = 0  # 消去したライン数

    def __init__(self, shape, color):
        self.x = GAME_AREA_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0
        self.shape = shape
        self.color = color


    # ブロックの描画
    def draw(self, game_area):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.color,
                                     (GAME_AREA_X + (self.x + x) * BLOCK_SIZE,
                                      GAME_AREA_Y + (self.y + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))

    # ブロックの移動
    def move(self, dx, dy, game_area):
        self.x += dx
        self.y += dy
        if not self.is_valid_position(game_area):
            self.x -= dx
            self.y -= dy
            return False
        return True

    # ブロックの回転
    def rotate(self, game_area, clockwise=True):
        # ブロックの形状を回転
        original_shape = self.shape
        if clockwise:
            self.shape = [list(row) for row in zip(*self.shape[::-1])]
        else:
            self.shape = [list(row) for row in zip(*self.shape)][::-1]

        # 回転後の位置が有効でない場合は元に戻す
        if not self.is_valid_position(game_area):
            self.shape = original_shape

    # 有効な位置かどうかを確認
    def is_valid_position(self, game_area, new_x=None, new_y=None):
        if new_x is None:
            new_x = self.x
        if new_y is None:
            new_y = self.y
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    if x + new_x < 0 or x + new_x >= GAME_AREA_WIDTH or y + new_y >= GAME_AREA_HEIGHT:
                        return False
                    if game_area[y + new_y][x + new_x]:
                        return False
        return True

    def drop_score(self, prey):
        # ドロップ得点の計算
        Block.score += self.y - prey





# メインゲームループ
def game_loop():
    running = True
    game_over = False
    game_area = [[0] * GAME_AREA_WIDTH for _ in range(GAME_AREA_HEIGHT)]
    current_block = Block(random.choice(list(tetromino_shapes.values())), random.choice(COLORS))
    last_fall_time = pygame.time.get_ticks()
    fall_speed = 2000  # ブロックの落下速度（ミリ秒）
    move_speed = 100  # ブロックの移動速度（ミリ秒）
    start_time = time.time()
    last_move_time = pygame.time.get_ticks()
    key_left_pressed = False
    key_right_pressed = False
    key_down_pressed = False
    next_block = Block(random.choice(list(tetromino_shapes.values())), random.choice(COLORS))


    while running and not game_over:
        elapsed_time = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    key_left_pressed = True
                elif event.key == pygame.K_d:
                    key_right_pressed = True
                elif event.key == pygame.K_s:
                    key_down_pressed = True
                elif event.key == pygame.K_s:
                    current_block.move(0, 1, game_area)  # 下に移動
                elif event.key == pygame.K_q:
                    current_block.rotate(game_area, clockwise=False)  # 左回転
                elif event.key == pygame.K_e:
                    current_block.rotate(game_area, clockwise=True)  # 右回転
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    key_left_pressed = False
                elif event.key == pygame.K_d:
                    key_right_pressed = False
                elif event.key == pygame.K_s:
                    key_down_pressed = False

        current_time = pygame.time.get_ticks()


        # 左右の連続移動
        if key_left_pressed and current_time - last_move_time > move_speed:
            current_block.move(-1, 0, game_area)
            last_move_time = current_time
        if key_right_pressed and current_time - last_move_time > move_speed:
            current_block.move(1, 0, game_area)
            last_move_time = current_time

            # ブロックの自動落下
        # ブロックの自動落下
        # ブロックの自動落下
        if current_time - last_fall_time > fall_speed:
            if not current_block.move(0, 1, game_area):
                fix_block_to_area(current_block, game_area)
                game_over = check_game_over(game_area)  # ゲームオーバーをチェック
                print(f"Game over check: {game_over}") # デバッグ出力
                if game_over:
                    print("Game Over!")#ゲームオーバーの処理
                    break  # ゲームオーバー時にループを抜ける
                else:
                    # 新しいブロックを生成
                    current_block = next_block
                    next_block = Block(random.choice(list(tetromino_shapes.values())), random.choice(COLORS))
                last_fall_time = current_time

        prey = current_block.y  # 現在の Y 座標を保存
        if key_down_pressed:
            prey = current_block.y  # 現在の Y 座標を保存
            while not current_block.move(0, 1, game_area):
                pass
            current_block.drop_score(prey)  # ドロップ得点を計算
            key_down_pressed = False  # ドロップ得点を計算

        # 次のブロックを表示する位置を指定
        next_block_position_x = SCREEN_WIDTH - SCORE_AREA_WIDTH + (
                    SCORE_AREA_WIDTH - (max([len(row) for row in next_block.shape]) * CELL_SIZE)) / 2
        next_block_position_y = 50  # または必要なY座標


        # ゲームエリアの描画
        screen.fill(WHITE)
        draw_game_area_border(screen, GAME_AREA_X, GAME_AREA_Y, GAME_AREA_PIXEL_WIDTH, GAME_AREA_PIXEL_HEIGHT,
                              (0, 0, 0), 4)
        # ゲームエリアとブロックの描画
        for y, row in enumerate(game_area):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell,
                                     (GAME_AREA_X + x * BLOCK_SIZE,
                                      GAME_AREA_Y + y * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
        current_block.draw(game_area)

        # UIの描画
        draw_ui(screen, next_block, elapsed_time, Block.score, Block.lines_cleared)

        # ゴーストブロックの描画
        draw_ghost_block(screen, current_block, game_area)

        pygame.display.update()
        clock.tick(60)
    pygame.quit()


game_loop()
