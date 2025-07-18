# 九宮格遊戲/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # 用於定義請求體的數據模型
from fastapi.staticfiles import StaticFiles # 新增: 導入 StaticFiles
from starlette.responses import HTMLResponse # 新增: 導入 HTMLResponse
import os # 新增: 導入 os 模組用於檢查檔案是否存在

app = FastAPI()

# 設置 CORS 讓您的前端網頁可以訪問這個後端
origins = [
    "http://localhost:8000",  # 如果您在本地運行前端伺服器
    "http://127.0.0.1:8000",
    "null",                  # 對於從本地檔案直接打開的瀏覽器 (file:///...)
    "http://127.0.0.1:5500"  # 如果您使用 VS Code 的 Live Server，它通常運行在 5500 端口
    # 當部署到 Cloud Run 後，您也可能需要在此處添加 Cloud Run 的 URL 作為允許的來源
    # 例如: "https://tic-119788516387.asia-east1.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================================
# 遊戲全局狀態 (請確保這些變數在應用啟動時被初始化)
# 9x9 的小格子棋盤，儲存 'X', 'O', 或 ' '
# 這裡將 game_board 視為一個列表的列表，其中每個子列表代表一個 3x3 大格子的所有 9 個小格子
# game_board[major_idx][minor_idx]
game_board: list[list[str]] = [[' ' for _ in range(9)] for _ in range(9)]

# 9 個大格子的狀態，儲存 'X', 'O', 'T' (平局), 或 ' ' (未完成)
big_board_status: list[str] = [' ' for _ in range(9)]

current_player: str = 'X' # 初始玩家為 'X'

# 下一個必須下棋的大格子索引 (0-8)。-1 表示任意大格子都可以下。
next_major_square: int = -1

# ====================================================================

# 輔助函式：檢查 3x3 棋盤的勝負
# 這個函數假設它接收的是一個 3x3 的二維列表 (例如 [['X', 'O', ' '], ...])
def check_win(board: list[list[str]]) -> str:
    """
    Check if there's a winner in a 3x3 board.
    Args:
        board: A 3x3 list of lists containing 'X', 'O', or ' ' (space)
    Returns:
        'X' if X wins, 'O' if O wins, 'T' if tie, ' ' if game is ongoing
    """
    # 檢查 rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != ' ':
            return board[i][0]
    
    # 檢查 columns
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != ' ':
            return board[0][i]
    
    # 檢查 diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
        return board[0][2]
    
    # Check for tie (no empty spaces left)
    is_full = all(cell != ' ' for row in board for cell in row)
    if is_full:
        return 'T'
    
    # Game is still ongoing
    return ' '

# 輔助函式：檢查整個大棋盤的勝負
# 這個函數的邏輯是正確的，因為 big_squares_status 已經是線性的 9 個狀態
# 它會將其轉換為 3x3 傳遞給 check_win
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

# 定義請求體的數據模型
class MoveRequest(BaseModel):
    major_idx: int
    minor_idx: int
    player: str

# 新增: 掛載靜態檔案目錄 (這應該是您的九宮格遊戲前端檔案所在的目錄)
# 因為您在 Dockerfile 中 COPY . /app，所以容器內的所有檔案都在 /app 目錄下
# 這裡的 "." 就代表容器內的 /app 目錄。
# 如果您的 test1.html 引用了 /css/style.css 或 /js/script.js，它們應該存放在 /app/css 或 /app/js
# 並且在 HTML 中以 /static/css/style.css 或 /static/js/script.js 引用。
# 如果所有前端檔案都只是單獨的 test1.html 而沒有其他靜態資源需要 /static 路徑，這行也可以省略。
app.mount("/static", StaticFiles(directory="."), name="static") 

# 新增: 處理根路徑 "/" 的請求，返回 test1.html 內容
@app.get("/", response_class=HTMLResponse)
async def read_root_html():
    html_file_path = "test1.html"
    # os.path.join 確保路徑格式正確，這裡 "." 表示當前工作目錄（即容器中的 /app）
    # 因為您的 Dockerfile COPY . /app，所以 test1.html 就在 /app 下
    full_path = os.path.join(os.getcwd(), html_file_path) 
    
    if not os.path.exists(full_path):
        # 如果檔案不存在，返回一個錯誤頁面
        return HTMLResponse(content=f"<html><body><h1>Error: {html_file_path} not found on server!</h1><p>Expected path: {full_path}</p></body></html>", status_code=404)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # 如果讀取檔案時發生其他錯誤
        return HTMLResponse(content=f"<html><body><h1>Error reading HTML file: {e}</h1></body></html>", status_code=500)


@app.get("/game/status")
async def get_game_status():
    global game_board, big_board_status, current_player, next_major_square
    
    # 返回當前遊戲狀態
    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square
    }

@app.post("/game/move")
async def make_move(move: MoveRequest):
    global game_board, big_board_status, current_player, next_major_square

    major_idx = move.major_idx
    minor_idx = move.minor_idx
    player = move.player

    # --- 遊戲邏輯驗證與處理 ---

    # 1. 檢查是否是當前玩家的回合
    if player != current_player:
        raise HTTPException(status_code=400, detail=f"現在是玩家 {current_player} 的回合")

    # 2. 檢查大格子的合法性
    if next_major_square != -1 and major_idx != next_major_square:
        raise HTTPException(status_code=400, detail=f"請在指定的大格 (索引 {next_major_square}) 下棋")

    # 3. 檢查大格子是否已被贏得或平局
    if big_board_status[major_idx] != ' ':
        raise HTTPException(status_code=400, detail=f"這個大格子 (索引 {major_idx}) 已經結束了，請選擇其他可用的格子。")

    # 4. 檢查小格子是否已被佔據
    # game_board 是一個列表的列表，每個子列表代表一個大格子的 9 個小格子
    # game_board[major_idx] 是對應大格子的 9 個小格子狀態
    if game_board[major_idx][minor_idx] != ' ':
        raise HTTPException(status_code=400, detail="這個小格子已被佔據，請選擇其他格子。")

    # --- 更新遊戲狀態 ---
    game_board[major_idx][minor_idx] = player

    # 修正: 提取當前大格子的 3x3 棋盤，以便傳入 check_win 函數
    current_big_square_cells_flat = game_board[major_idx]
    temp_3x3_board_for_check_win = [
        current_big_square_cells_flat[0:3],
        current_big_square_cells_flat[3:6],
        current_big_square_cells_flat[6:9]
    ]

    big_square_winner = check_win(temp_3x3_board_for_check_win) # 使用修正後的 3x3 棋盤
    if big_square_winner != ' ':
        big_board_status[major_idx] = big_square_winner # 更新大格子的狀態
        
    # --- 決定下一個玩家和下一個大格子 ---
    
    # 檢查整體遊戲是否結束 (在大棋盤上判斷勝負或平局)
    overall_winner = check_overall_win(big_board_status) # 使用 big_board_status 判斷
    if overall_winner != ' ':
        # 遊戲結束
        next_major_square = -2 # 用 -2 表示遊戲結束，無下一格
        current_player = ' ' # 清空當前玩家
        return {
            "board": game_board,
            "big_squares": big_board_status,
            "player": current_player,
            "next_square": next_major_square,
            "message": f"遊戲結束！{'平局' if overall_winner == 'T' else f'玩家 {overall_winner} 獲勝！'}"
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