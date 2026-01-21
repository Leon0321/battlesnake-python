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
                next_oppo_body = list(cur_oppo_body)
                if(next_1ndex not in my_food):
                    del next_my_body[len(next_my_body) - 1]
                if((next_1ndex not in oppo_body) and (next_1ndex not in next_my_body[1:])):
                    index_list[next_index[0]][next_index[1]] = turn+1
                    if(len(next_oppo_body) > 0):
                        del next_oppo_body[len(next_oppo_body) - 1]
                    q.append((next_index[0], next_index[1], turn+1, next_my_body, next_oppo_body))
    return index_list

def BFS_fastest(game_state, my_body, oppo_body, fturn, start, goal):
    q = [(start[0], start[1], 0, [])]
    visited = set()
    visited.add((start[0], start[1]))
    index4 = [[0, 1], [0, -1], [-1, 0], [1, 0]]
    directions = ["up", "down", "left", "right"]
    while q:
        curr_x, curr_y, turn, path = q.pop(0)
        if curr_x == goal[0] and curr_y == goal[1]:
            return path
        if turn >= fturn: continue
        for i, (dx, dy) in enumerate(index4):
            nx, ny = curr_x + dx, curr_y + dy
            next_pos = {"x": nx, "y": ny}
            if not (0 <= nx < 11 and 0 <= ny < 11): continue
            remaining_body = my_body[:max(1, len(my_body) - turn - 1)]
            if next_pos in remaining_body: continue
            if next_pos in oppo_body: continue
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                new_path = path + [directions[i]]
                q.append((nx, ny, turn + 1, new_path))
    return []

def floodfill_space(start_x, start_y, my_body, oppo_body, max_depth=20):
    """指定位置から到達可能な空間をカウント + 出口の広さも評価"""
    visited = set()
    queue = [(start_x, start_y, 0)]
    visited.add((start_x, start_y))
    count = 0
    exit_spaces = 0  # 遠い場所（出口）のマス数
    
    while queue:
        x, y, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        count += 1
        
        # 深い位置（出口エリア）のマスを重視
        if depth > max_depth * 0.6:
            exit_spaces += 1
        
        for dx, dy in [[0,1], [0,-1], [1,0], [-1,0]]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 11 and 0 <= ny < 11:
                pos = {"x": nx, "y": ny}
                if (nx, ny) not in visited:
                    if pos not in my_body and pos not in oppo_body:
                        visited.add((nx, ny))
                        queue.append((nx, ny, depth + 1))
    
    # 出口が狭い袋小路は低評価（出口スペースが少ないとペナルティ）
    return count + exit_spaces * 3


def evaluate_space_after_enemy_move(my_next_pos, my_body, enemy_head, enemy_body, food_positions):
    """
    自分が次のマスに行った後、敵が最適に動いた場合の自分の空間を評価
    相手に袋小路を作られるリスクを検出
    """
    # 敵が移動できる4方向
    enemy_possible_moves = [
        {"x": enemy_head["x"], "y": enemy_head["y"] + 1},
        {"x": enemy_head["x"], "y": enemy_head["y"] - 1},
        {"x": enemy_head["x"] - 1, "y": enemy_head["y"]},
        {"x": enemy_head["x"] + 1, "y": enemy_head["y"]}
    ]
    
    worst_space = 999  # 最悪のケース（敵が最適に動いた場合）の空間
    
    for enemy_next in enemy_possible_moves:
        # 敵の次の位置が有効かチェック
        if not (0 <= enemy_next["x"] < 11 and 0 <= enemy_next["y"] < 11):
            continue
        if enemy_next in enemy_body[:-1]:  # 尻尾以外との衝突チェック
            continue
        
        # 敵が餌を食べるかチェック
        enemy_eats_food = enemy_next in food_positions
        
        # 敵の新しい体を計算
        if enemy_eats_food:
            # 餌を食べたら尻尾は消えない
            future_enemy_body = [enemy_next] + enemy_body
        else:
            # 餌を食べなければ尻尾が消える
            future_enemy_body = [enemy_next] + enemy_body[:-1]
        
        # 自分の新しい体を計算（自分も餌を食べる可能性）
        my_eats_food = my_next_pos in food_positions
        if my_eats_food:
            future_my_body = [my_next_pos] + my_body
        else:
            future_my_body = [my_next_pos] + my_body[:-1]
        
        # この状況での自分の空間を計算（深めに探索）
        space = floodfill_space(
            my_next_pos["x"], 
            my_next_pos["y"], 
            future_my_body, 
            future_enemy_body, 
            max_depth=30  # より深く探索
        )
        
        # 敵の最適手（自分にとって最悪）を探す
        if space < worst_space:
            worst_space = space
    
    return worst_space


def detect_narrow_corridors(start_x, start_y, my_body, oppo_body, max_depth=25):
    """
    幅1マスの通路（危険な形状）を検出
    戻り値: (空間の広さ, 狭い通路のマス数, 平均幅)
    """
    visited = set()
    queue = [(start_x, start_y, 0)]
    visited.add((start_x, start_y))
    
    total_count = 0
    narrow_corridor_count = 0  # 幅1マスの通路のマス数
    width_sum = 0
    
    while queue:
        x, y, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        
        total_count += 1
        
        # このマスの「幅」を計算（隣接する空きマスの数）
        adjacent_free = 0
        for dx, dy in [[0,1], [0,-1], [1,0], [-1,0]]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 11 and 0 <= ny < 11:
                pos = {"x": nx, "y": ny}
                if pos not in my_body and pos not in oppo_body:
                    adjacent_free += 1
        
        # 幅の判定（隣接する空きマスが2つ以下=狭い通路）
        if adjacent_free <= 2:
            narrow_corridor_count += 1
        
        width_sum += adjacent_free
        
        # 次のマスを探索
        for dx, dy in [[0,1], [0,-1], [1,0], [-1,0]]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 11 and 0 <= ny < 11:
                pos = {"x": nx, "y": ny}
                if (nx, ny) not in visited:
                    if pos not in my_body and pos not in oppo_body:
                        visited.add((nx, ny))
                        queue.append((nx, ny, depth + 1))
    
    avg_width = width_sum / total_count if total_count > 0 else 0
    corridor_ratio = narrow_corridor_count / total_count if total_count > 0 else 0
    
    return total_count, narrow_corridor_count, avg_width, corridor_ratio




def evaluate_center_control(x, y):
    """
    中央(5,5)からの距離を評価
    戻り値: 中央に近いほど高スコア
    """
    center_x, center_y = 5, 5
    distance_to_center = abs(x - center_x) + abs(y - center_y)
    
    # 中央に近いほど高スコア（最大10、最小0）
    center_bonus = max(0, 10 - distance_to_center)
    
    return center_bonus


def is_enemy_at_edge(enemy_head):
    """
    敵が端（壁から2マス以内）にいるか判定
    """
    edge_threshold = 2
    
    at_left_edge = enemy_head["x"] <= edge_threshold
    at_right_edge = enemy_head["x"] >= 10 - edge_threshold
    at_top_edge = enemy_head["y"] <= edge_threshold
    at_bottom_edge = enemy_head["y"] >= 10 - edge_threshold
    
    return at_left_edge or at_right_edge or at_top_edge or at_bottom_edge


def calculate_trap_position(my_head, enemy_head, enemy_body):
    """
    敵を端に追い込むための「幅1の通路」を作る位置を計算
    戦略: 敵の逃げ道を1マスの通路に限定する位置に配置
    """
    enemy_x = enemy_head["x"]
    enemy_y = enemy_head["y"]
    
    # 敵がどの壁に近いか判定
    dist_to_left = enemy_x
    dist_to_right = 10 - enemy_x
    dist_to_top = enemy_y
    dist_to_bottom = 10 - enemy_y
    
    min_wall_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)
    
    # 最も近い壁の方向に押し付ける
    if min_wall_dist == dist_to_left:
        # 左壁に押し付ける → 自分は敵の右側に壁を作る
        trap_x = enemy_x + 1  # 敵の1マス右
        trap_y = enemy_y
        print(f"Trapping enemy against LEFT wall at ({trap_x}, {trap_y})")
    
    elif min_wall_dist == dist_to_right:
        # 右壁に押し付ける → 自分は敵の左側に壁を作る
        trap_x = enemy_x - 1
        trap_y = enemy_y
        print(f"Trapping enemy against RIGHT wall at ({trap_x}, {trap_y})")
    
    elif min_wall_dist == dist_to_top:
        # 上壁に押し付ける → 自分は敵の下側に壁を作る
        trap_x = enemy_x
        trap_y = enemy_y + 1
        print(f"Trapping enemy against TOP wall at ({trap_x}, {trap_y})")
    
    else:  # dist_to_bottom
        # 下壁に押し付ける → 自分は敵の上側に壁を作る
        trap_x = enemy_x
        trap_y = enemy_y - 1
        print(f"Trapping enemy against BOTTOM wall at ({trap_x}, {trap_y})")
    
    # 範囲チェック
    if 0 <= trap_x <= 10 and 0 <= trap_y <= 10:
        return {"x": trap_x, "y": trap_y}
    else:
        # 範囲外なら敵の頭を返す
        return enemy_head


def should_prioritize_center(my_head, enemy_head, my_length, enemy_length, board_health):
    """
    中央陣取りを優先すべきか判定
    """
    # 序盤（ターン50以下）かつ体力が十分（70以上）
    # 敵が中央にいない（中央5x5エリア外）
    enemy_in_center = (3 <= enemy_head["x"] <= 7) and (3 <= enemy_head["y"] <= 7)
    my_in_center = (3 <= my_head["x"] <= 7) and (3 <= my_head["y"] <= 7)
    
    # 体力が十分で、敵が中央を占拠していない場合
    if board_health > 70 and not enemy_in_center:
        return True
    
    # 自分が既に中央にいて、敵より長い場合は中央キープ
    if my_in_center and my_length >= enemy_length:
        return True
    
    return False



def get_best_target(game_state, my_head, my_body, target_head, target_body):
    """敵を幅1マスの通路に追い込む戦略"""
    directions = [
        {"x": target_head["x"], "y": target_head["y"] + 1, "name": "up"},
        {"x": target_head["x"], "y": target_head["y"] - 1, "name": "down"},
        {"x": target_head["x"] - 1, "y": target_head["y"], "name": "left"},
        {"x": target_head["x"] + 1, "y": target_head["y"], "name": "right"}
    ]
    
    enemy_escape_routes = []
    for pos in directions:
        if 0 <= pos["x"] < 11 and 0 <= pos["y"] < 11:
            if {"x": pos["x"], "y": pos["y"]} not in target_body:
                # その方向の空間と形状を評価
                space = floodfill_space(pos["x"], pos["y"], target_body, my_body, max_depth=20)
                
                # **新規**: 敵の逃げ道の通路の幅を評価
                total, narrow_count, avg_width, corridor_ratio = detect_narrow_corridors(
                    pos["x"], pos["y"], target_body, my_body, max_depth=20
                )
                
                enemy_escape_routes.append({
                    "pos": {"x": pos["x"], "y": pos["y"]},
                    "space": space,
                    "narrow_count": narrow_count,
                    "avg_width": avg_width,
                    "corridor_ratio": corridor_ratio,
                    "distance": abs(pos["x"] - my_head["x"]) + abs(pos["y"] - my_head["y"])
                })
    
    if not enemy_escape_routes:
        return target_head
    
    # **新規戦略1**: 敵の逃げ道が「幅1マスの通路」なら優先的に追い込む
    narrow_corridor_routes = [r for r in enemy_escape_routes if r["corridor_ratio"] > 0.6]
    if narrow_corridor_routes:
        # 最も狭い通路に追い込む
        best_trap = max(narrow_corridor_routes, key=lambda r: r["corridor_ratio"])
        print(f"Forcing enemy into narrow corridor! Ratio: {best_trap['corridor_ratio']:.2f}")
        return best_trap["pos"]
    
    # **戦略2**: 敵の逃げ道が1つしかない
    if len(enemy_escape_routes) == 1:
        print(f"Enemy has only 1 escape! Blocking it")
        return enemy_escape_routes[0]["pos"]
    
    # **戦略3**: 敵の最も狭い逃げ道を塞ぐ
    narrowest_escape = min(enemy_escape_routes, key=lambda r: r["space"])
    enemy_length = len(target_body)
    if narrowest_escape["space"] < enemy_length * 1.5:
        print(f"Can trap enemy! Narrowest space: {narrowest_escape['space']}")
        return narrowest_escape["pos"]
    
    # **戦略4**: 平均幅が最も狭い逃げ道を塞ぐ
    narrowest_width_route = min(enemy_escape_routes, key=lambda r: r["avg_width"])
    if narrowest_width_route["avg_width"] < 2.5:
        print(f"Blocking narrow width route! Width: {narrowest_width_route['avg_width']:.2f}")
        return narrowest_width_route["pos"]
    
    # デフォルト: 広い逃げ道のうち自分に近いものを塞ぐ
    widest_escape = max(enemy_escape_routes, key=lambda r: r["space"])
    wide_routes = [r for r in enemy_escape_routes if r["space"] >= widest_escape["space"] * 0.7]
    closest_wide = min(wide_routes, key=lambda r: r["distance"])
    return closest_wide["pos"]


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
    # 安全な餌がない場合、距離が近い餌を選ぶ（リスクあり）
        reachable_food = [f for f in food_list if my_dist_map[f['x']][f['y']] < 100]
        if reachable_food:
            return min(reachable_food, key=lambda f: my_dist_map[f['x']][f['y']])
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
        "head": "cosmic-horror",  # TODO: Choose head
        "tail": "cosmic-horror",  # TODO: Choose tail
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
    #初期化
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
    
    #首を省く
    if my_neck["y"] > my_head["y"]:  
        is_move_safe["up"] = False
    elif my_neck["y"] < my_head["y"]:  
        is_move_safe["down"] = False
    elif my_neck["x"] < my_head["x"]: 
        is_move_safe["left"] = False
    elif my_neck["x"] > my_head["x"]:  
        is_move_safe["right"] = False
    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    #壁を省く
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
    #自分の体（長さ三以上の尻尾以外）を省く
    if my_head_u in my_body:
        is_move_safe["up"] = False
        if my_length > 2 and (my_body[my_length-1] == my_head_u) and board_health < 100 and my_turn > 1:
            is_move_safe["up"] = True
    if my_head_d in my_body:
        is_move_safe["down"] = False
        if my_length > 2 and(my_body[my_length-1] == my_head_d) and board_health < 100 and my_turn > 1:
            is_move_safe["down"] = True
    if my_head_l in my_body:
        is_move_safe["left"] = False
        if my_length > 2 and (my_body[my_length-1] == my_head_l) and board_health < 100 and my_turn > 1:
            is_move_safe["left"] = True
    if my_head_r in my_body:
        is_move_safe["right"] = False
        if my_length > 2 and (my_body[my_length-1] == my_head_r) and board_health < 100 and my_turn > 1:
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

    #敵の体を省く
    if my_head_u in target_body:
        is_move_safe["up"] = False
    if my_head_d in target_body:
        is_move_safe["down"] = False
    if my_head_l in target_body:
        is_move_safe["left"] = False
    if my_head_r in target_body:
        is_move_safe["right"] = False

    #敵の次の位置を例外でペナルティ計算
    enemy_adjacent_penalty = {"up": 0, "down": 0, "left": 0, "right": 0}

    # まず敵より短い場合、敵の頭の隣を完全にブロック
    if my_length <= len(target_body):
        if my_head_u in target_nextbody:
            is_move_safe["up"] = False
        if my_head_d in target_nextbody:
            is_move_safe["down"] = False
        if my_head_l in target_nextbody:
            is_move_safe["left"] = False
        if my_head_r in target_nextbody:
            is_move_safe["right"] = False
    
        # 他の3方向が全部即死の場合だけ、敵の隣も許可する（最終手段）
        remaining_safe = [move for move, safe in is_move_safe.items() if safe]
        if len(remaining_safe) == 0:
            # 全滅なので敵の隣でも行くしかない
            if my_head_u in target_nextbody:
                is_move_safe["up"] = True
            if my_head_d in target_nextbody:
                is_move_safe["down"] = True
            if my_head_l in target_nextbody:
                is_move_safe["left"] = True
            if my_head_r in target_nextbody:
                is_move_safe["right"] = True
    else:
        # 敵より長い場合は積極的に向かう（ペナルティなし）
        if my_head_u in target_nextbody:
            enemy_adjacent_penalty["up"] = 0
        if my_head_d in target_nextbody:
            enemy_adjacent_penalty["down"] = 0
        if my_head_l in target_nextbody:
            enemy_adjacent_penalty["left"] = 0
        if my_head_r in target_nextbody:
            enemy_adjacent_penalty["right"] = 0

    # Are there any safe moves left?

    #各方向のture,falseから行けるところのみを抽出
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    #詰んでたらしかたない
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    
    #floodfillで各方向の安全性を評価
    move_safety_scores = {}
    move_positions = {"up": my_head_u,"down": my_head_d,"left": my_head_l,"right": my_head_r}

    for move in safe_moves:
        pos = move_positions[move]
    
        # 現在の空間評価
        current_space = floodfill_space(pos["x"], pos["y"], my_body, target_body, max_depth=my_length + 15)
    
        # 通路の形状を検出
        total_space, narrow_count, avg_width, corridor_ratio = detect_narrow_corridors(
            pos["x"], pos["y"], my_body, target_body, max_depth=my_length + 10
        )
    
        # 敵が最適に動いた後の空間評価
        food_positions = game_state['board']['food']
        future_space = evaluate_space_after_enemy_move(pos, my_body, target_head, target_body, food_positions)
    
        # 敵が動いた後の通路形状も評価
        future_my_body = [pos] + my_body[:-1]
        future_narrow_space, future_narrow_count, future_avg_width, future_corridor_ratio = detect_narrow_corridors(
            pos["x"], pos["y"], future_my_body, target_body, max_depth=my_length + 10
        )
    
        # 空間の広さを計算
        space = min(current_space, future_space * 1.2)
    
        penalty = enemy_adjacent_penalty.get(move, 0)

        # 空間が体長より小さい場合は減点
        if space < my_length * 1.2:
            penalty += (my_length * 1.2 - space) * 5
    
        # 未来の空間が狭い場合は減点
        if future_space < my_length * 1.5:
            danger_level = (my_length * 1.5 - future_space) * 20
            penalty += danger_level
            print(f"Move {move} creates dead-end risk! Future space: {future_space}, penalty: {danger_level}")
        
            if future_space < my_length:
                penalty += 500
                print(f"Move {move} is DEADLY! Space: {future_space} < Length: {my_length}")
    
        # **新規**: 狭い通路（幅1マス）の割合が高い場合は大幅減点
        if corridor_ratio > 0.5:
            corridor_penalty = corridor_ratio * 200
            penalty += corridor_penalty
            print(f"Move {move} leads to narrow corridor! Ratio: {corridor_ratio:.2f}, penalty: {corridor_penalty}")
    
        # **新規**: 未来の通路がさらに狭くなる場合は超減点
        if future_corridor_ratio > 0.6:
            future_corridor_penalty = future_corridor_ratio * 300
            penalty += future_corridor_penalty
            print(f"Move {move} leads to FUTURE narrow corridor! Ratio: {future_corridor_ratio:.2f}, penalty: {future_corridor_penalty}")
    
        # **新規**: 平均幅が狭い（2.5以下）場合も減点
        if avg_width < 2.5:
            width_penalty = (2.5 - avg_width) * 50
            penalty += width_penalty
            print(f"Move {move} has narrow avg width: {avg_width:.2f}, penalty: {width_penalty}")

        move_safety_scores[move] = space - penalty
    #最も安全なルートがあれば優先
    if move_safety_scores:
        safest_moves = [m for m in safe_moves if move_safety_scores[m] == max(move_safety_scores.values())]
        if len(safest_moves) > 0:
            safe_moves = safest_moves
    # Choose a random move from the safe ones
    # next_move = random.choice(safe_moves)



    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
        if next_move in safe_moves:
            # FloodFillで評価した結果も確認
            if next_move in move_safety_scores:
                # ルートの次の手が極端に危険でないか確認
                route_score = move_safety_scores[next_move]
                max_score = max(move_safety_scores.values())
                # スコアが最大の半分以下なら危険なのでルートを破棄
                if route_score < max_score * 0.5:
                    print(f"Route {next_move} too dangerous (score: {route_score} vs max: {max_score}), using safe move")
                    route_list = []
                    next_move = random.choice(safe_moves)
            print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
            print(f"MOVE {game_state['turn']}: {next_move}")
            return {"move": next_move}
        else:
            route_list = []

    #目的ますを決める
    
    # 戦略判定: 中央陣取りを優先すべきか
    prioritize_center = should_prioritize_center(my_head, target_head, my_length, len(target_body), board_health)
    
    # 敵が端にいるか判定
    enemy_at_edge = is_enemy_at_edge(target_head)
    
    # モード1: 敵より十分長い 攻撃モード
    if len(target_body) + 2 < len(my_body):
        # 敵が端にいる場合は詰め戦略
        if enemy_at_edge:
            target = calculate_trap_position(my_head, target_head, target_body)
            print(f"TRAP MODE: Enemy at edge, setting trap at ({target['x']}, {target['y']})")
        else:
            # 敵を端に追い込む
            target = get_best_target(game_state, my_head, my_body, target_head, target_body)
            print(f"ATTACK MODE: Pushing enemy to edge")
    
    # モード2: 中央陣取り優先
    elif prioritize_center:
        center_x, center_y = 5, 5
        # 既に中央にいる場合は餌を取る
        my_distance_to_center = abs(my_head["x"] - center_x) + abs(my_head["y"] - center_y)
        if my_distance_to_center <= 2:
            # 中央エリア内にいるので餌取り
            target = determine_food(game_state)
            if target is None:
                target = {"x": center_x, "y": center_y}
                print(f"CENTER CONTROL: Staying in center")
        else:
            # 中央に向かう
            target = {"x": center_x, "y": center_y}
            print(f"MOVING TO CENTER: Distance = {my_distance_to_center}")
    
    # モード3: 餌取り優先
    else:
        target = determine_food(game_state)
        if target is None:
            # 餌がない場合は中央へ
            center_x, center_y = 5, 5
            target = {"x": center_x, "y": center_y}
            print(f"No safe food, heading to center")
        
    obstacle_body = target_body[1:]
    
    route_list = BFS_fastest(game_state, my_body, obstacle_body, 100, [my_head["x"], my_head["y"]], [target["x"], target["y"]])
    print(route_list)

    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
        print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
        print(f"MOVE {game_state['turn']}: {next_move}")
        return {"move": next_move}
    else:
        next_move = random.choice(safe_moves)

    print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}
# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})











