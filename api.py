# 九宮格遊戲/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles # 引入 StaticFiles (如果還有其他靜態檔案如CSS/JS)
from pydantic import BaseModel
import os # 引入 os 模組用於檔案路徑操作

app = FastAPI()

# 設置 CORS 讓您的前端網頁可以訪問這個後端
# 請根據您的 Cloud Run 前端實際部署 URL 添加到這裡
# 如果前端和後端是同一個 Cloud Run 服務，則可以包含其自身的 URL
origins = [
    "http://localhost:8000",   # 如果您在本地運行前端伺服器
    "http://127.0.0.1:8000",
    "null",                    # 對於從本地檔案直接打開的瀏覽器 (file:///...)
    "http://127.0.0.1:5500",   # 如果您使用 VS Code 的 Live Server，它通常運行在 5500 端口
    "https://tic-119788516387.asia-east1.run.app" # 請確認這是您的 Cloud Run 服務的實際 URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================================
# 遊戲全局狀態
# 9x9 的小格子棋盤，儲存 'X', 'O', 或 ' '
# 結構為：一個包含 9 個列表的列表，每個列表代表一個大格子內的 9 個小格子
# game_board[major_idx][minor_idx]
game_board: list[list[str]] = [[' ' for _ in range(9)] for _ in range(9)]

# 9 個大格子的狀態，儲存 'X', 'O', 'T' (平局), 或 ' ' (未完成)
big_board_status: list[str] = [' ' for _ in range(9)]

current_player: str = 'X' # 初始玩家為 'X'

# 下一個必須下棋的大格子索引 (0-8)。-1 表示任意大格子都可以下。
next_major_square: int = -1

# ====================================================================

def check_win(board_slice: list[list[str]]) -> str:
    """
    Check if there's a winner in a 3x3 board slice.
    Args:
        board_slice: A 3x3 list of lists containing 'X', 'O', or ' ' (space)
                     e.g., [['X', ' ', 'O'], [' ', 'X', ' '], ['O', ' ', 'X']]
    Returns:
        'X' if X wins, 'O' if O wins, 'T' if tie, ' ' if game is ongoing
    """
    # 這裡的 board_slice 應該已經是一個 3x3 的結構，直接進行判斷

    # 檢查 rows
    for i in range(3):
        if board_slice[i][0] == board_slice[i][1] == board_slice[i][2] and board_slice[i][0] != ' ':
            return board_slice[i][0]
    
    # 檢查 columns
    for i in range(3):
        if board_slice[0][i] == board_slice[1][i] == board_slice[2][i] and board_slice[0][i] != ' ':
            return board_slice[0][i]
    
    # 檢查 diagonals
    if board_slice[0][0] == board_slice[1][1] == board_slice[2][2] and board_slice[0][0] != ' ':
        return board_slice[0][0]
    if board_slice[0][2] == board_slice[1][1] == board_slice[2][0] and board_slice[0][2] != ' ':
        return board_slice[0][2]
    
    # Check for tie (no empty spaces left)
    is_full = all(cell != ' ' for row in board_slice for cell in row)
    if is_full:
        return 'T'
    
    # Game is still ongoing
    return ' '

# 定義請求體的數據模型
class MoveRequest(BaseModel):
    major_idx: int
    minor_idx: int
    player: str

# 輔助函式：檢查整個大棋盤的勝負
def check_overall_win(big_squares_status: list[str]) -> str:
    """
    Check if there's a winner or tie on the main 3x3 big board.
    Args:
        big_squares_status: A list of 9 strings representing the status of big squares.
    Returns:
        'X' if X wins, 'O' if O wins, 'T' if tie, ' ' if game is ongoing
    """
    # 轉換為 3x3 棋盤以便於使用 check_win 邏輯
    temp_big_board = [
        big_squares_status[0:3],
        big_squares_status[3:6],
        big_squares_status[6:9]
    ]
    return check_win(temp_big_board) # 複用 check_win 邏輯

# 輔助函式：獲取遊戲結束訊息
def get_game_over_message() -> str:
    overall_winner = check_overall_win(big_board_status)
    if overall_winner != ' ':
        return f"遊戲結束！{'平局' if overall_winner == 'T' else f'玩家 {overall_winner} 獲勝！'}"
    return "" # 遊戲未結束，返回空字串

# --- API 路由 ---

# 提供前端 HTML 檔案
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 確保 test1.html 檔案存在於 Docker 容器內正確的路徑
    # 假設 test1.html 與 api.py 在同一個目錄下
    file_path = os.path.join(os.path.dirname(__file__), "test1.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return FileResponse(file_path) # 直接返回 FileResponse，讓FastAPI處理檔案讀取和響應頭
    except FileNotFoundError:
        # 如果找不到檔案，返回 404 錯誤
        raise HTTPException(status_code=404, detail=f"Frontend HTML file not found at {file_path}. Please ensure test1.html is copied to the container.")


@app.get("/game/status")
async def get_game_status():
    global game_board, big_board_status, current_player, next_major_square
    
    # 返回當前遊戲狀態
    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square,
        "message": get_game_over_message() # 增加一個函數來獲取遊戲結束訊息
    }

@app.post("/game/reset")
async def reset_game():
    global game_board, big_board_status, current_player, next_major_square

    # 重置所有遊戲狀態變數
    game_board = [[' ' for _ in range(9)] for _ in range(9)]
    big_board_status = [' ' for _ in range(9)]
    current_player = 'X'
    next_major_square = -1

    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square,
        "message": "遊戲已重置！玩家 X 先手。"
    }

@app.post("/game/move")
async def make_move(move: MoveRequest):
    global game_board, big_board_status, current_player, next_major_square

    major_idx = move.major_idx
    minor_idx = move.minor_idx
    player = move.player

    # 檢查遊戲是否已經結束
    game_over_message = get_game_over_message()
    if game_over_message:
        raise HTTPException(status_code=400, detail=game_over_message)

    # --- 遊戲邏輯驗證與處理 ---

    # 1. 檢查是否是當前玩家的回合
    if player != current_player:
        raise HTTPException(status_code=400, detail=f"現在是玩家 {current_player} 的回合")

    # 2. 檢查大格子的合法性
    if next_major_square != -1 and major_idx != next_major_square:
        raise HTTPException(status_code=400, detail=f"請在指定的大格 (索引 {next_major_square}) 下棋")

    # 3. 檢查大格子是否已被贏得或平局
    if big_board_status[major_idx] != ' ':
        # 如果 next_major_square 是 -1 (任意下棋)，但選到了已結束的大格
        if next_major_square == -1:
            raise HTTPException(status_code=400, detail=f"這個大格子 (索引 {major_idx}) 已經結束了，請選擇其他可用的格子。")
        else:
            # 理論上，如果 next_major_square 不為 -1 且等於 major_idx，
            # 並且 big_board_status[major_idx] != ' '，
            # 這表示遊戲狀態有邏輯錯誤或前端未正確禁用。
            raise HTTPException(status_code=400, detail=f"指定的格子 (索引 {major_idx}) 已結束。")

    # 4. 檢查小格子是否已被佔據
    if game_board[major_idx][minor_idx] != ' ':
        raise HTTPException(status_code=400, detail="這個小格子已被佔據，請選擇其他格子。")

    # --- 更新遊戲狀態 ---
    game_board[major_idx][minor_idx] = player

    # 檢查當前小格子所在的大格子是否被贏得或平局
    current_big_square_cells = game_board[major_idx] # 這會拿到一個包含9個元素的列表
    temp_3x3_board = [
        current_big_square_cells[0:3], # 大格子內第一行
        current_big_square_cells[3:6], # 大格子內第二行
        current_big_square_cells[6:9]  # 大格子內第三行
    ]

    big_square_winner = check_win(temp_3x3_board)
    if big_square_winner != ' ':
        big_board_status[major_idx] = big_square_winner # 更新大格子的狀態
        
    # --- 決定下一個玩家和下一個大格子 ---
    
    # 檢查整體遊戲是否結束 (在大棋盤上判斷勝負或平局)
    overall_winner_status = check_overall_win(big_board_status)
    if overall_winner_status != ' ':
        # 遊戲結束
        next_major_square = -1 # 統一設為 -1，讓前端判斷 message 來禁用
        current_player = ' ' # 清空當前玩家
        message = f"遊戲結束！{'平局' if overall_winner_status == 'T' else f'玩家 {overall_winner_status} 獲勝！'}"
        return {
            "board": game_board,
            "big_squares": big_board_status,
            "player": current_player,
            "next_square": next_major_square,
            "message": message
        }

    # 決定下一個大格子
    # 如果剛才下的小格子所對應的大格子 (minor_idx) 已經被贏得或平局
    # 則 next_major_square 變為 -1 (任意選擇)
    if big_board_status[minor_idx] != ' ':
        next_major_square = -1
    else:
        next_major_square = minor_idx # 下一個玩家必須在 minor_idx 對應的大格下棋

    # 切換玩家
    current_player = 'O' if current_player == 'X' else 'X'

    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square,
        "message": "移動成功！"
    }