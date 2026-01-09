# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com
import random
import typing

route_list = []


def BFS(game_state: typing.Dict, my_head, my_body, oppo_body):
    my_food = game_state['board']['food']
    index_list = [[100 for _ in range(11)] for _ in range(11)]
    # リストの全マスを100で埋める
    q = []
    index4 = [[0,1], [0,-1], [-1,0], [1,0]]
    index_list[my_head["x"]][my_head["y"]] = 0
    q.append((my_head["x"], my_head["y"], 0, my_body, oppo_body))
    #以下から各方向を見て行けそうなマスの探索を開始
    while(len(q) > 0):
        start_x, start_y, turn, my_cur_body, cur_oppo_body= q.pop(0)
        for dir in range(len(index4)):
            next_index = [start_x + index4[dir][0], start_y + index4[dir][1]]
            if(next_index[0] > -1 and next_index[0] < 11 and next_index[1] > -1 and next_index[1] < 11 and index_list[next_index[0]][next_index[1]] > turn+1):
                next_1ndex = {"x":next_index[0], "y":next_index[1]}
                next_my_body = [next_1ndex] + my_cur_body
                next_oppo_body = cur_oppo_body
                if(next_1ndex not in my_food):
                    del next_my_body[len(next_my_body) - 1]
                if(next_1ndex not in oppo_body and next_1ndex not in next_my_body[1:]):
                    index_list[next_index[0]][next_index[1]] = turn+1
                    del next_oppo_body[len(next_oppo_body) - 1]
                    q.append((next_index[0], next_index[1], turn+1, next_my_body, next_oppo_body))
    return index_list

def BFS_fastest(game_state: typing.Dict, my_body, oppo_body, fturn, start, goal):
    my_food = game_state['board']['food']
    index_list = [[100 for _ in range(11)] for _ in range(11)]
    q = []
    route = []
    index4 = [[0,1], [0,-1], [-1,0], [1,0]]
    index_list[start[0]][start[1]] = 0
    q.append((start[0], start[1], 0, my_body, oppo_body, route))
    #以下から各方向を見て行けそうなマスの探索を開始
    while(len(q) > 0):
        start_x, start_y, turn, my_cur_body, cur_oppo_body, cur_route= q.pop(0)
        for dir in range(len(index4)):
            next_index = [start_x + index4[dir][0], start_y + index4[dir][1]]
            if(next_index[0] > -1 and next_index[0] < 11 and next_index[1] > -1 and next_index[1] < 11 and index_list[next_index[0]][next_index[1]] > turn+1):
                next_1ndex = {"x":next_index[0], "y":next_index[1]}
                next_my_body = [next_1ndex] + my_cur_body
                next_oppo_body = list(cur_oppo_body)
                if(next_1ndex not in my_food):
                    del next_my_body[len(next_my_body) - 1]
                if(next_1ndex not in next_oppo_body and next_1ndex not in next_my_body[1:]):
                    index_list[next_index[0]][next_index[1]] = turn+1
                    del next_oppo_body[len(next_oppo_body) - 1]
                next_route = list(cur_route)
                if(dir == 0):
                    next_route.append("up")
                elif(dir == 1):
                    next_route.append("down")
                elif(dir == 2):
                    next_route.append("left")
                elif(dir == 3):
                    next_route.append("right")
                if(next_index[0] == goal[0] and next_index[1] == goal[1] and turn+1 <= fturn):
                    route_list = next_route
                    return route_list
                q.append((next_index[0], next_index[1], turn+1, next_my_body, next_oppo_body, next_route))
    return []

def get_foodlist(game_state: typing.Dict):
    my_food = game_state['board']['food']
    food_list = []
    for food in range(len(my_food)):
        food_index = {"x":my_food[food]["x"], "y":my_food[food]["y"], "d":100}
        food_list.append(food_index)
    return food_list

def calculate_distance(game_state: typing.Dict, food_list: typing.Dict):
    my_id = game_state["you"]["id"]
    snakes = game_state["board"]["snakes"]
    opponent = None
    for snake in snakes:
        if snake["id"] != my_id:
            opponent = snake
            break
    distance = BFS(game_state, game_state["you"]["body"][0], game_state["you"]["body"], opponent["body"])
    for food in food_list:
        food["d"] = distance[food["x"]][food["y"]]
    return food_list

def filtering_food(game_state: typing.Dict, food_list):
    # 自分を取得
    my_id = game_state["you"]["id"]
    my_body = game_state["you"]["body"]
    my_head = my_body[0]
    my_length = game_state["you"]["length"]
    # 敵の特定
    snakes = game_state["board"]["snakes"]
    opponent = [s for s in snakes if s["id"] != my_id][0]
    op_body = opponent["body"]
    op_head = op_body[0]
    op_length = opponent["length"]
    my_dist_map = BFS(game_state, my_head, my_body, op_body)
    op_dist_map = BFS(game_state, op_head, op_body, my_body)
    # 以下フィルタリング
    safe_food_list = []
    for food in food_list:
        my_dist = my_dist_map[food['x']][food['y']]
        op_dist = op_dist_map[food['x']][food['y']]
        if my_dist >= 100:
            continue
        # 敵も到達不可能な場所なら、自分が近づけばいいので距離999にしとく
        if op_dist >= 100:
            op_dist = 999
        # 敵より有利か
        is_closer = False
        if my_dist < op_dist:
            is_closer = True
        elif my_dist == op_dist:
            if my_length > op_length:
                is_closer = True
        if not is_closer:
            continue
        # 空間チェック
        space_count = 0
        queue = [food]
        visited = {(food['x'], food['y'])}
        while queue:
            curr = queue.pop(0)
            curr_dist = my_dist_map[curr['x']][curr['y']]
            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                nx, ny = curr['x'] + d[0], curr['y'] + d[1]
                if 0 <= nx < 11 and 0 <= ny < 11:
                    n_dist = my_dist_map[nx][ny]
                    # 波紋が奥へ進んでいるマスだけをカウント
                    if n_dist < 100 and n_dist > curr_dist:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append({'x': nx, 'y': ny})
                            space_count += 1
        if space_count > my_length:
            safe_food_list.append(food)
    # 候補が一つもない場合は None
    if not safe_food_list:
        return None
    # ここまで残った餌は全て敵より近くかつ安全、その中で一番近いものを選ぶ
    best_food = None
    min_dist = 999
    # リストの中から最短を探す
    candidates = []
    for f in safe_food_list:
        d = my_dist_map[f['x']][f['y']]
        if d < min_dist:
            min_dist = d
            candidates = [f]
        elif d == min_dist:
            candidates.append(f)
    #　最短のえさが複数あったら欄d無で返す
    if candidates:
        return random.choice(candidates)
    return None
 
    # 最小距離 d を持つものを選択
    min_distance_food = min(safe_food_list, key=lambda food: food.get('d', float('inf')))
    min_distance = min_distance_food.get('d', float('inf'))
    # 同じ距離ならランダム
    same_distance_foods = [f for f in safe_food_list if f.get('d', float('inf')) == min_distance]
    return random.choice(same_distance_foods)

def determine_food(game_state: typing.Dict):
    foodlist = get_foodlist(game_state)

    foodlist = calculate_distance(game_state, foodlist)

    return filtering_food(game_state, foodlist)

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")
    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#C61B1B",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }
# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")
# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")
# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    global route_list
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
    my_length = game_state['you']['length']
    my_turn = game_state['turn']
    board_health = game_state['you']['health']
    my_head_u = {"x": my_head["x"] , "y": my_head["y"] + 1}
    my_head_d = {"x": my_head["x"] , "y": my_head["y"] - 1}
    my_head_l = {"x": my_head["x"] - 1, "y": my_head["y"]}
    my_head_r = {"x": my_head["x"] + 1, "y": my_head["y"]}
    
    if my_neck["y"] > my_head["y"]:  # Neck is left of head, don't move left
        is_move_safe["up"] = False
    elif my_neck["y"] < my_head["y"]:  # Neck is right of head, don't move right
        is_move_safe["down"] = False
    elif my_neck["x"] < my_head["x"]:  # Neck is below head, don't move down
        is_move_safe["left"] = False
    elif my_neck["x"] > my_head["x"]:  # Neck is above head, don't move up
        is_move_safe["right"] = False
    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds

    if my_head_u["y"] > 10:
        is_move_safe["up"] = False
    if my_head_d["y"] < 0:
        is_move_safe["down"] = False
    if my_head_l["x"] < 0:
        is_move_safe["left"] = False
    if my_head_r["x"] > 10:
        is_move_safe["right"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']

    if my_head_u in my_body:
        is_move_safe["up"] = False
        if (my_body[my_length-1] == my_head_u) and board_health < 100 and my_turn > 1:
            is_move_safe["up"] = True
    if my_head_d in my_body:
        is_move_safe["down"] = False
        if (my_body[my_length-1] == my_head_d) and board_health < 100 and my_turn > 1:
            is_move_safe["down"] = True
    if my_head_l in my_body:
        is_move_safe["left"] = False
        if (my_body[my_length-1] == my_head_l) and board_health < 100 and my_turn > 1:
            is_move_safe["left"] = True
    if my_head_r in my_body:
        is_move_safe["right"] = False
        if (my_body[my_length-1] == my_head_r) and board_health < 100 and my_turn > 1:
            is_move_safe["right"] = True

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    # opponents = game_state['board']['snakes']

    target_body = [
        cell
        for snake in game_state['board']['snakes']
        if snake['id'] != game_state["you"]["id"]
        for cell in snake['body']
    ]
    target_head = target_body[0]
    target_nextbody = [{"x": target_head["x"] , "y": target_head["y"] + 1}, {"x": target_head["x"] , "y": target_head["y"] - 1}, {"x": target_head["x"] - 1, "y": target_head["y"]}, {"x": target_head["x"] + 1, "y": target_head["y"]}]

    if my_head_u in target_body or my_head_u in target_nextbody:
        is_move_safe["up"] = False
    if my_head_d in target_body or my_head_d in target_nextbody:
        is_move_safe["down"] = False
    if my_head_l in target_body or my_head_l in target_nextbody:
        is_move_safe["left"] = False
    if my_head_r in target_body or my_head_r in target_nextbody:
        is_move_safe["right"] = False

    # Are there any safe moves left?

    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    # Choose a random move from the safe ones
    # next_move = random.choice(safe_moves)

    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
        if next_move in safe_moves:
            return {"move": next_move}
        else:
            route_list = []


    if len(target_body) + 2 < len(my_body):
        # 敵にぶつかりにいく
        target = target_head
    else:
        # エサ取り優先
        target = determine_food(game_state)
        if target is None: # 餌が見つからない場合
            return {"move": random.choice(safe_moves)}
        
    obstacle_body = target_body[1:]
    
    route_list = BFS_fastest(game_state, my_body, obstacle_body, 100, [my_head["x"], my_head["y"]], [target["x"], target["y"]])

    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
        return {"move": next_move}
    else:
        next_move = random.choice(safe_moves)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}
# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})