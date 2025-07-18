# 九宮格遊戲/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles # 導入 StaticFiles
from starlette.responses import HTMLResponse # 導入 HTMLResponse
import os # 導入 os 模組用於檢查檔案是否存在

app = FastAPI()

# 設置 CORS 讓您的前端網頁可以訪問這個後端
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
    "http://127.0.0.1:5500"
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
game_board: list[list[str]] = [[' ' for _ in range(9)] for _ in range(9)]
big_board_status: list[str] = [' ' for _ in range(9)]
current_player: str = 'X'
next_major_square: int = -1

# ====================================================================

# 輔助函式：檢查 3x3 棋盤的勝負
def check_win(board: list[list[str]]) -> str:
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != ' ':
            return board[i][0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != ' ':
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
        return board[0][2]
    
    is_full = all(cell != ' ' for row in board for cell in row)
    if is_full:
        return 'T'
    return ' '

# 輔助函式：檢查整個大棋盤的勝負
def check_overall_win(big_squares_status: list[str]) -> str:
    temp_big_board = [
        big_squares_status[0:3],
        big_squares_status[3:6],
        big_squares_status[6:9]
    ]
    return check_win(temp_big_board)

# 定義請求體的數據模型
class MoveRequest(BaseModel):
    major_idx: int
    minor_idx: int
    player: str

# 新增: 掛載靜態檔案目錄 (這應該是您的九宮格遊戲前端檔案所在的目錄)
# 因為您在 Dockerfile 中 COPY . /app，所以容器內的所有檔案都在 /app 目錄下
# 這裡的 "." 就代表容器內的 /app 目錄。
app.mount("/static", StaticFiles(directory="."), name="static") 

# 覆蓋原有的 "/" 根路徑，讓它返回 test1.html 內容
@app.get("/", response_class=HTMLResponse)
async def read_root_html():
    html_file_path = "test1.html"
    full_path = os.path.join(os.getcwd(), html_file_path) 
    
    if not os.path.exists(full_path):
        return HTMLResponse(content=f"<html><body><h1>Error: {html_file_path} not found on server!</h1><p>Expected path: {full_path}</p></body></html>", status_code=404)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error reading HTML file: {e}</h1></body></html>", status_code=500)


# 您原有的 /game/status 路由 (這將保持不變，因為上面的修改只影響根路徑)
@app.get("/game/status")
async def get_game_status():
    global game_board, big_board_status, current_player, next_major_square
    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square
    }

# 您原有的 /game/move 路由 (這也將保持不變)
@app.post("/game/move")
async def make_move(move: MoveRequest):
    global game_board, big_board_status, current_player, next_major_square

    major_idx = move.major_idx
    minor_idx = move.minor_idx
    player = move.player

    if player != current_player:
        raise HTTPException(status_code=400, detail=f"現在是玩家 {current_player} 的回合")

    if next_major_square != -1 and major_idx != next_major_square:
        raise HTTPException(status_code=400, detail=f"請在指定的大格 (索引 {next_major_square}) 下棋")

    if big_board_status[major_idx] != ' ':
        raise HTTPException(status_code=400, detail=f"這個大格子 (索引 {major_idx}) 已經結束了，請選擇其他可用的格子。")

    if game_board[major_idx][minor_idx] != ' ':
        raise HTTPException(status_code=400, detail="這個小格子已被佔據，請選擇其他格子。")

    game_board[major_idx][minor_idx] = player

    current_big_square_cells_flat = game_board[major_idx]
    temp_3x3_board_for_check_win = [
        current_big_square_cells_flat[0:3],
        current_big_square_cells_flat[3:6],
        current_big_square_cells_flat[6:9]
    ]

    big_square_winner = check_win(temp_3x3_board_for_check_win)
    if big_square_winner != ' ':
        big_board_status[major_idx] = big_square_winner
        
    overall_winner = check_overall_win(big_board_status)
    if overall_winner != ' ':
        next_major_square = -2
        current_player = ' '
        return {
            "board": game_board,
            "big_squares": big_board_status,
            "player": current_player,
            "next_square": next_major_square,
            "message": f"遊戲結束！{'平局' if overall_winner == 'T' else f'玩家 {overall_winner} 獲勝！'}"
        }

    if big_board_status[minor_idx] != ' ':
        next_major_square = -1
    else:
        next_major_square = minor_idx

    current_player = 'O' if current_player == 'X' else 'X'

    return {
        "board": game_board,
        "big_squares": big_board_status,
        "player": current_player,
        "next_square": next_major_square,
        "message": "移動成功！"
    }