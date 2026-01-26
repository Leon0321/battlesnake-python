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


def floodfill(start_pos, game_state, my_body, oppo_body):
    #指定位置から到達可能なマス数をカウント（安全性評価用）
    visited = set()
    queue = [(start_pos['x'], start_pos['y'])]
    visited.add((start_pos['x'], start_pos['y']))
    count = 0
    
    while queue:
        x, y = queue.pop(0)
        count += 1
        
        for dx, dy in [[0,1], [0,-1], [1,0], [-1,0]]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not (0 <= nx < 11 and 0 <= ny < 11):
                continue
            
            next_pos = {"x": nx, "y": ny}
            # 自分の体と敵の体を障害物として扱う
            if next_pos in my_body or next_pos in oppo_body:
                continue
            
            visited.add((nx, ny))
            queue.append((nx, ny))
    
    return count


def evaluate_position_safety(pos, game_state, my_snake, enemy_snake):
    #置の安全性を数値で評価（高いほど安全）
    score = 0
    my_body = my_snake['body']
    enemy_body = enemy_snake['body']
    enemy_head = enemy_snake['head']
    my_length = my_snake['length']
    enemy_length = enemy_snake['length']
    
    #Floodfill
    reachable = floodfill(pos, game_state, my_body, enemy_body)
    score += reachable * 10
    
    #中央への近さ
    center_dist = abs(pos['x'] - 5) + abs(pos['y'] - 5)
    score += (10 - center_dist) * 3
    
    #敵の頭と長さとの比較
    enemy_dist = abs(pos['x'] - enemy_head['x']) + abs(pos['y'] - enemy_head['y'])
    length_diff = my_length - enemy_length
    
    if length_diff > 0:
        my_center_dist = abs(pos['x'] - 5) + abs(pos['y'] - 5)
        enemy_center_dist = abs(enemy_head['x'] - 5) + abs(enemy_head['y'] - 5)
        
        if my_center_dist < enemy_center_dist:
            score += 50
        
        if 2 <= enemy_dist <= 6:
            score += 40  
        elif enemy_dist < 2:
            score += 20  
        elif enemy_dist > 7:
            score -= 30 
    else:
        if 2 <= enemy_dist <= 4:
            score += 20  
        elif enemy_dist < 2:
            score -= 10 
        else:
            score += enemy_dist * 2 
    
    #壁近
    wall_dist = min(pos['x'], pos['y'], 10 - pos['x'], 10 - pos['y'])
    score += wall_dist * 2
    
    return score

def is_narrow_path(pos, game_state, my_body, enemy_body, enemy_head):
    #幅1の危険な経路かどうかを判定
    my_length = len(my_body)
    
    reachable = floodfill(pos, game_state, my_body, enemy_body)
    if reachable < my_length:
        return True
    if reachable < my_length * 2:
        return True
    if reachable < 15:
        return True
    
    #敵が動いてふさがれるのを考慮
    enemy_next_positions = [
        {'x': enemy_head['x'], 'y': enemy_head['y'] + 1},
        {'x': enemy_head['x'], 'y': enemy_head['y'] - 1},
        {'x': enemy_head['x'] - 1, 'y': enemy_head['y']},
        {'x': enemy_head['x'] + 1, 'y': enemy_head['y']}
    ]
    
    min_reachable_after_enemy_move = reachable
    for enemy_next_pos in enemy_next_positions:
        if not (0 <= enemy_next_pos['x'] < 11 and 0 <= enemy_next_pos['y'] < 11):continue

        if enemy_next_pos in enemy_body or enemy_next_pos in my_body:continue
        
        simulated_enemy_body = [enemy_next_pos] + enemy_body[:-1]
        
        reachable_after = floodfill(pos, game_state, my_body, simulated_enemy_body)
        min_reachable_after_enemy_move = min(min_reachable_after_enemy_move, reachable_after)

    if min_reachable_after_enemy_move < my_length:
        return True

    if min_reachable_after_enemy_move < my_length * 1.5:
        return True
    
    enemy_dist = abs(pos['x'] - enemy_head['x']) + abs(pos['y'] - enemy_head['y'])
    if enemy_dist <= 2 and reachable < 20:
        return True
    
    return False

def find_enemy_narrow_corridor(enemy_head, enemy_body, my_body, game_state):
    #敵が幅1の経路にいるか（さっきの攻撃側パターンの検知）
    reachable = floodfill(enemy_head, game_state, enemy_body, my_body)
    
    if reachable < 8:
        exits = find_corridor_exits(enemy_head, enemy_body, my_body, game_state)
        if len(exits) > 0:
            return {'in_corridor': True,'exits': exits,'reachable_area': reachable}
    return None


def find_corridor_exits(start_pos, enemy_body, my_body, game_state):
    #幅1経路の出口（広い空間への入り口）を見つける
    exits = []
    visited = set()
    queue = [(start_pos['x'], start_pos['y'])]
    visited.add((start_pos['x'], start_pos['y']))
    
    while queue:
        x, y = queue.pop(0)
        pos = {'x': x, 'y': y}
        
        local_reachable = floodfill(pos, game_state, enemy_body, my_body)
        
        if local_reachable > 15:
            exits.append(pos)
            continue 
        
        for dx, dy in [[0,1], [0,-1], [1,0], [-1,0]]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not (0 <= nx < 11 and 0 <= ny < 11):
                continue
            
            next_pos = {'x': nx, 'y': ny}
            if next_pos in enemy_body[1:] or next_pos in my_body:
                continue
            
            visited.add((nx, ny))
            queue.append((nx, ny))
    
    return exits


def calculate_blocking_position(my_head, exits):
    #敵の幅１出口を塞ぐための最適な位置を発見
    if not exits:
        return None
    
    closest_exit = min(exits, key=lambda e: abs(my_head['x'] - e['x']) + abs(my_head['y'] - e['y']))
    
    return closest_exit


def predict_enemy_escape_routes(enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state):
    # 敵の脱出経路を予測し、塞ぐべき位置を返す（先ほどまでに加えてさらに攻撃性能を高めるために）
    escape_routes = []
    
    if edge_type == 'left':
        for dy in [-1, 0, 1]:
            escape_pos = {'x': parallel_line, 'y': enemy_head['y'] + dy}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'right':
        for dy in [-1, 0, 1]:
            escape_pos = {'x': parallel_line, 'y': enemy_head['y'] + dy}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'bottom':
        for dx in [-1, 0, 1]:
            escape_pos = {'x': enemy_head['x'] + dx, 'y': parallel_line}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'top':
        for dx in [-1, 0, 1]:
            escape_pos = {'x': enemy_head['x'] + dx, 'y': parallel_line}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    return escape_routes


def is_being_trapped(my_head, my_body, enemy_head, enemy_body, game_state):
    #自分が追い詰められているかどうか（安全性評価の足しに）
    #移動可能領域や敵の位置を考慮して行う

    my_reachable = floodfill(my_head, game_state, my_body, enemy_body)
    my_length = len(my_body)

    if my_reachable < my_length:
        return True, 3 

    if my_reachable < my_length * 1.5:
        return True, 2 

    if my_reachable < my_length * 2:
        return True, 1  

    enemy_dist = abs(my_head['x'] - enemy_head['x']) + abs(my_head['y'] - enemy_head['y'])
    if enemy_dist <= 2 and my_reachable < my_length * 2.5:
        return True, 1
    
    return False, 0


def can_effectively_trap_enemy(my_head, my_body, enemy_head, enemy_body, enemy_snake, game_state):
    # 敵を的確に追い詰められるかどうかを判定（意味なく近づくだけじゃ意味ないし逆に不利になる）

    my_length = len(my_body)
    enemy_length = len(enemy_body)

    if my_length < enemy_length:
        return False, 0
    
    enemy_reachable = floodfill(enemy_head, game_state, enemy_body, my_body)
    
    if enemy_reachable < enemy_length:
        return True, 3 
    
    enemy_wall_dist = min(enemy_head['x'], enemy_head['y'],
                          10 - enemy_head['x'], 10 - enemy_head['y'])
    
    my_center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
    
    if enemy_wall_dist <= 3 and my_center_dist <= 4:
        herding_opportunity = detect_wall_herding_opportunity(enemy_head, enemy_body, my_head, my_body, game_state)
        if herding_opportunity:
            my_safe_space = herding_opportunity.get('my_safe_space', 0)
            enemy_trapped_space = herding_opportunity.get('enemy_trapped_space', 999)
            
            if my_safe_space >= my_length + 5 and enemy_trapped_space < enemy_length * 2:
                return True, 2
    
    if enemy_wall_dist <= 5 and my_length >= enemy_length:
        return True, 1  
    
    return False, 0


def is_safe_food(food_pos, my_head, my_body, enemy_head, enemy_body, game_state, *, relaxed: bool = False):
    #餌の安全性をさらに評価（餌をとったときに生まれる隙を軽減するため

    food_wall_dist = min(food_pos['x'], food_pos['y'],
                         10 - food_pos['x'], 10 - food_pos['y'])
    
    if not relaxed:
        if food_wall_dist <= 2:
            return False
    else:
        if food_wall_dist <= 1:
            return False
    
    food_reachable = floodfill(food_pos, game_state, my_body, enemy_body)
    my_length = len(my_body)

    if not relaxed and food_reachable < my_length:
        return False
    if relaxed and food_reachable < max(5, int(my_length * 0.8)):
        return False
    
    food_enemy_dist = abs(food_pos['x'] - enemy_head['x']) + abs(food_pos['y'] - enemy_head['y'])
    if food_enemy_dist <= (2 if not relaxed else 1):
        if len(my_body) <= len(enemy_body):
            return False
    
    return True


def choose_food_target(game_state: typing.Dict, my_head, my_body, enemy_head, enemy_body, *, relaxed: bool) -> typing.Optional[typing.Dict]:
    #最適な餌選び（ditermineより安全性など向上）
    foods = game_state['board']['food']
    if not foods:
        return None

    dist_map = BFS(game_state, my_head, my_body, enemy_body)

    candidates: list[typing.Dict] = []
    for f in foods:
        d = dist_map[f['x']][f['y']]
        if d >= 100:
            continue
        if not is_safe_food(f, my_head, my_body, enemy_head, enemy_body, game_state, relaxed=relaxed):
            continue
        candidates.append({'x': f['x'], 'y': f['y'], 'd': d})

    if not candidates:
        return None

    min_d = min(c['d'] for c in candidates)
    best = [c for c in candidates if c['d'] == min_d]
    pick = random.choice(best)
    return {'x': pick['x'], 'y': pick['y']}


def threatened_squares_by_head(my_next_head: typing.Dict, *, my_length: int, enemy_length: int) -> list[typing.Dict]:
    #自分の体で領域を文d難する
    if my_length <= enemy_length:
        return []
    xs = [
        {'x': my_next_head['x'], 'y': my_next_head['y'] + 1},
        {'x': my_next_head['x'], 'y': my_next_head['y'] - 1},
        {'x': my_next_head['x'] - 1, 'y': my_next_head['y']},
        {'x': my_next_head['x'] + 1, 'y': my_next_head['y']},
    ]
    out: list[typing.Dict] = []
    for p in xs:
        if 0 <= p['x'] < 11 and 0 <= p['y'] < 11:
            out.append(p)
    return out


def territory_delta_score(game_state: typing.Dict, *, my_next_head: typing.Dict, my_body: list[typing.Dict], enemy_head: typing.Dict, enemy_body: list[typing.Dict], my_length: int, enemy_length: int) -> int:
    #分断の有効性を評価する（領域さ差）

    my_area = floodfill(my_next_head, game_state, my_body, enemy_body)

    threat = threatened_squares_by_head(my_next_head, my_length=my_length, enemy_length=enemy_length)

    enemy_area = floodfill(enemy_head, game_state, enemy_body + threat, my_body)

    center_dist = abs(my_next_head['x'] - 5) + abs(my_next_head['y'] - 5)
    center_bonus = (10 - center_dist) * 2

    return (my_area - enemy_area) * 6 + center_bonus


def predict_enemy_next_move(enemy_head, enemy_body, my_body, game_state):
    #敵の次の動きを予測（相手の動き方知らんが、汎用的に最も可能性の高い方向を返す）

    possible_moves = []
    directions = [
        {'x': enemy_head['x'], 'y': enemy_head['y'] + 1, 'dir': 'up'},
        {'x': enemy_head['x'], 'y': enemy_head['y'] - 1, 'dir': 'down'},
        {'x': enemy_head['x'] - 1, 'y': enemy_head['y'], 'dir': 'left'},
        {'x': enemy_head['x'] + 1, 'y': enemy_head['y'], 'dir': 'right'}
    ]
    
    for move in directions:
        pos = {'x': move['x'], 'y': move['y']}
        if not (0 <= pos['x'] < 11 and 0 <= pos['y'] < 11):
            continue
        if pos in enemy_body[1:] or pos in my_body:
            continue
        
        reachable = floodfill(pos, game_state, enemy_body, my_body)
        possible_moves.append({
            'pos': pos,
            'dir': move['dir'],
            'reachable': reachable
        })
    
    if not possible_moves:
        return None
    
    # 最も到達可能領域が大きい方向を選ぶ（敵は安全な方向に動く）
    best_move = max(possible_moves, key=lambda m: m['reachable'])
    return best_move['pos']


def predict_enemy_escape_routes(enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state): 
    #敵の脱出経路を予測し、ふさぐ
    escape_routes = []
    
    if edge_type == 'left':
        for dy in [-1, 0, 1]:
            escape_pos = {'x': parallel_line, 'y': enemy_head['y'] + dy}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    # この位置から中央への到達可能性をチェック
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'right':
        for dy in [-1, 0, 1]:
            escape_pos = {'x': parallel_line, 'y': enemy_head['y'] + dy}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'bottom':
        for dx in [-1, 0, 1]:
            escape_pos = {'x': enemy_head['x'] + dx, 'y': parallel_line}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    elif edge_type == 'top':
        for dx in [-1, 0, 1]:
            escape_pos = {'x': enemy_head['x'] + dx, 'y': parallel_line}
            if 0 <= escape_pos['x'] < 11 and 0 <= escape_pos['y'] < 11:
                if escape_pos not in enemy_body and escape_pos not in my_body:
                    reachable = floodfill(escape_pos, game_state, enemy_body, my_body)
                    if reachable > len(enemy_body):
                        escape_routes.append(escape_pos)
    
    return escape_routes

def calculate_blocking_position(my_head, exits):
    if not exits:
        return None
    
    closest_exit = min(exits, key=lambda e: abs(my_head['x'] - e['x']) + abs(my_head['y'] - e['y']))

    return closest_exit


def detect_wall_herding_opportunity(enemy_head, enemy_body, my_head, my_body, game_state):
    #並走戦略

    enemy_wall_dist = min(enemy_head['x'], enemy_head['y'], 
                          10 - enemy_head['x'], 10 - enemy_head['y'])

    if enemy_wall_dist > 5:
        return None 
    
    edge_type = None
    parallel_line = None  
    
    if enemy_head['x'] <= 2:
        edge_type = 'left'
        parallel_line = 3 
    elif enemy_head['x'] >= 8:
        edge_type = 'right'
        parallel_line = 7
    elif enemy_head['y'] <= 2:
        edge_type = 'bottom'
        parallel_line = 3  
    elif enemy_head['y'] >= 8:
        edge_type = 'top'
        parallel_line = 7 
    else:
        return None
    
    is_positioned = False
    if edge_type in ['left', 'right']:
        if edge_type == 'left' and my_head['x'] >= parallel_line:
            is_positioned = True
        elif edge_type == 'right' and my_head['x'] <= parallel_line:
            is_positioned = True
    else:
        if edge_type == 'bottom' and my_head['y'] >= parallel_line:
            is_positioned = True
        elif edge_type == 'top' and my_head['y'] <= parallel_line:
            is_positioned = True
    
    my_safe_space = 0
    enemy_trapped_space = 0
    
    if edge_type == 'left':
        test_pos_mine = {'x': parallel_line + 1, 'y': 5}
        my_safe_space = floodfill(test_pos_mine, game_state, my_body, enemy_body)
        
        test_pos_enemy = {'x': parallel_line - 1, 'y': enemy_head['y']}
        enemy_trapped_space = floodfill(test_pos_enemy, game_state, enemy_body, my_body)
        
    elif edge_type == 'right':
        test_pos_mine = {'x': parallel_line - 1, 'y': 5}
        my_safe_space = floodfill(test_pos_mine, game_state, my_body, enemy_body)
        
        test_pos_enemy = {'x': parallel_line + 1, 'y': enemy_head['y']}
        enemy_trapped_space = floodfill(test_pos_enemy, game_state, enemy_body, my_body)
        
    elif edge_type == 'bottom':
        test_pos_mine = {'x': 5, 'y': parallel_line + 1}
        my_safe_space = floodfill(test_pos_mine, game_state, my_body, enemy_body)
        
        test_pos_enemy = {'x': enemy_head['x'], 'y': parallel_line - 1}
        enemy_trapped_space = floodfill(test_pos_enemy, game_state, enemy_body, my_body)
        
    elif edge_type == 'top':
        test_pos_mine = {'x': 5, 'y': parallel_line - 1}
        my_safe_space = floodfill(test_pos_mine, game_state, my_body, enemy_body)
        
        test_pos_enemy = {'x': enemy_head['x'], 'y': parallel_line + 1}
        enemy_trapped_space = floodfill(test_pos_enemy, game_state, enemy_body, my_body)
    
    my_length = len(my_body)
    if my_safe_space < my_length + 10:
        print(f"Herding aborted: insufficient safe space ({my_safe_space} < {my_length + 10})")
        return None

    enemy_length = len(enemy_body)
    if enemy_trapped_space > enemy_length + 10:
        print(f"Herding not effective: enemy has too much space ({enemy_trapped_space})")
        return None

    
    return {'type': 'wall_herding','edge_type': edge_type,'parallel_line': parallel_line,'is_positioned': is_positioned,'enemy_wall_dist': enemy_wall_dist,'my_safe_space': my_safe_space,'enemy_trapped_space': enemy_trapped_space}


def calculate_parallel_chase_position(my_head, enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state):
    #並走位置を計算。(相手の退路を塞ぎつつ、中央への退路を確保)

    if edge_type == 'left':
        target_x = parallel_line
        target_y = enemy_head['y']
        
        if my_head['x'] >= parallel_line:
            target_y = enemy_head['y']
            if my_head['y'] == enemy_head['y']:
                if enemy_head['y'] < 5:  
                    target_y = enemy_head['y'] + 1  
                else:  
                    target_y = enemy_head['y'] - 1  
            elif abs(my_head['y'] - enemy_head['y']) > 0:
                if my_head['y'] < enemy_head['y']:
                    target_y = my_head['y'] + 1
                else:
                    target_y = my_head['y'] - 1
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'right':
        target_x = parallel_line
        target_y = enemy_head['y']

        if my_head['x'] <= parallel_line:
            target_y = enemy_head['y']
            if my_head['y'] == enemy_head['y']:
                if enemy_head['y'] < 5:
                    target_y = enemy_head['y'] + 1
                else:
                    target_y = enemy_head['y'] - 1
            elif abs(my_head['y'] - enemy_head['y']) > 0:
                if my_head['y'] < enemy_head['y']:
                    target_y = my_head['y'] + 1
                else:
                    target_y = my_head['y'] - 1
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'bottom':
        target_x = enemy_head['x']
        target_y = parallel_line

        if my_head['y'] >= parallel_line:
            target_x = enemy_head['x']
            if my_head['x'] == enemy_head['x']:
                if enemy_head['x'] < 5: 
                    target_x = enemy_head['x'] + 1  
                else:
                    target_x = enemy_head['x'] - 1 
            elif abs(my_head['x'] - enemy_head['x']) > 0:
                if my_head['x'] < enemy_head['x']:
                    target_x = my_head['x'] + 1
                else:
                    target_x = my_head['x'] - 1
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'top':
        target_x = enemy_head['x']
        target_y = parallel_line

        if my_head['y'] <= parallel_line:
            target_x = enemy_head['x']
            if my_head['x'] == enemy_head['x']:
                if enemy_head['x'] < 5:
                    target_x = enemy_head['x'] + 1
                else:
                    target_x = enemy_head['x'] - 1
            elif abs(my_head['x'] - enemy_head['x']) > 0:
                if my_head['x'] < enemy_head['x']:
                    target_x = my_head['x'] + 1
                else:
                    target_x = my_head['x'] - 1
        
        return {'x': target_x, 'y': target_y}
    
    return None


def plan_attack_strategy(game_state, my_head, my_body, enemy_head, enemy_body, enemy_snake):
    # 攻撃戦略決定し、目標マス返す
    my_length = len(my_body)
    enemy_length = len(enemy_body)
    
    can_trap, trap_quality = can_effectively_trap_enemy(my_head, my_body, enemy_head, enemy_body, enemy_snake, game_state)
    if not can_trap:
        return None
    
    # 戦略1: 敵が幅1経路にいるか確認
    corridor_info = find_enemy_narrow_corridor(enemy_head, enemy_body, my_body, game_state)
    if corridor_info and corridor_info['in_corridor']:
        blocking_pos = calculate_blocking_position(my_head, corridor_info['exits'])
        if blocking_pos:
            print(f"STRATEGY: Blocking corridor exit at {blocking_pos}")
            return blocking_pos
    
    predicted_enemy_pos = predict_enemy_next_move(enemy_head, enemy_body, my_body, game_state)
    if predicted_enemy_pos:
        enemy_wall_dist = min(predicted_enemy_pos['x'], predicted_enemy_pos['y'],
                              10 - predicted_enemy_pos['x'], 10 - predicted_enemy_pos['y'])
        if enemy_wall_dist <= 3:
            if predicted_enemy_pos['x'] <= 2:
                intercept_pos = {'x': 3, 'y': predicted_enemy_pos['y']}
            elif predicted_enemy_pos['x'] >= 8:
                intercept_pos = {'x': 7, 'y': predicted_enemy_pos['y']}
            elif predicted_enemy_pos['y'] <= 2:
                intercept_pos = {'x': predicted_enemy_pos['x'], 'y': 3}
            elif predicted_enemy_pos['y'] >= 8:
                intercept_pos = {'x': predicted_enemy_pos['x'], 'y': 7}
            else:
                intercept_pos = None
            
            if intercept_pos:
                intercept_space = floodfill(intercept_pos, game_state, my_body, enemy_body)
                if intercept_space >= len(my_body):
                    print(f"STRATEGY: Intercepting enemy at {intercept_pos}")
                    return intercept_pos
    herding_opportunity = detect_wall_herding_opportunity(enemy_head, enemy_body, my_head, my_body, game_state)
    if herding_opportunity:
        edge_type = herding_opportunity['edge_type']
        parallel_line = herding_opportunity['parallel_line']
        is_positioned = herding_opportunity['is_positioned']
        my_safe_space = herding_opportunity.get('my_safe_space', 0)
        enemy_trapped_space = herding_opportunity.get('enemy_trapped_space', 999)

        if my_safe_space < len(my_body) + 5:  
            print(f"ABORT: My safe space too small, returning to normal strategy")
            return None
        
        if not is_positioned:
            if edge_type in ['left', 'right']:
                target = {'x': parallel_line, 'y': enemy_head['y']}
            else:
                target = {'x': enemy_head['x'], 'y': parallel_line}

            return target
        
        parallel_pos = calculate_parallel_chase_position(
            my_head, enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state
        )
        
        escape_routes = predict_enemy_escape_routes(enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state)
        if escape_routes:
            closest_escape = min(escape_routes, key=lambda e: abs(my_head['x'] - e['x']) + abs(my_head['y'] - e['y']))
            if edge_type == 'left':
                blocking_pos = {'x': closest_escape['x'] + 1, 'y': closest_escape['y']}
            elif edge_type == 'right':
                blocking_pos = {'x': closest_escape['x'] - 1, 'y': closest_escape['y']}
            elif edge_type == 'bottom':
                blocking_pos = {'x': closest_escape['x'], 'y': closest_escape['y'] + 1}
            elif edge_type == 'top':
                blocking_pos = {'x': closest_escape['x'], 'y': closest_escape['y'] - 1}

            block_space = floodfill(blocking_pos, game_state, my_body, enemy_body)
            if block_space >= len(my_body) and 0 <= blocking_pos['x'] < 11 and 0 <= blocking_pos['y'] < 11:
                return blocking_pos
        
        if parallel_pos:
            return parallel_pos
    
    if trap_quality >= 2:

        enemy_distances = {'left': enemy_head['x'],'right': 10 - enemy_head['x'],'bottom': enemy_head['y'],'top': 10 - enemy_head['y']}
        
        nearest_edge = min(enemy_distances.items(), key=lambda x: x[1])
        edge_name = nearest_edge[0]
        edge_dist = nearest_edge[1]

        if edge_dist <= 4:
            if edge_name == 'left':
                push_target = {'x': min(enemy_head['x'] + 2, 6), 'y': enemy_head['y']}
            elif edge_name == 'right':
                push_target = {'x': max(enemy_head['x'] - 2, 4), 'y': enemy_head['y']}
            elif edge_name == 'bottom':
                push_target = {'x': enemy_head['x'], 'y': min(enemy_head['y'] + 2, 6)}
            elif edge_name == 'top':
                push_target = {'x': enemy_head['x'], 'y': max(enemy_head['y'] - 2, 4)}
            
            push_space = floodfill(push_target, game_state, my_body, enemy_body)
            if push_space >= my_length:
                return push_target

    center = {'x': 5, 'y': 5}
    my_center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
    enemy_center_dist = abs(enemy_head['x'] - 5) + abs(enemy_head['y'] - 5)
    enemy_dist = abs(my_head['x'] - enemy_head['x']) + abs(my_head['y'] - enemy_head['y'])
    
    if my_center_dist < enemy_center_dist and my_center_dist <= 3 and 3 <= enemy_dist <= 5:
        return center
    
    if enemy_dist > 6 and my_center_dist > 2:
        return center
    
    return None

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
        # 敵も到達不可能な場所なら、自分が近づければいいので距離999にしとく
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
            # ★★★ 追加：端っこすぎる餌は避ける ★★★
            food_wall_dist = min(food['x'], food['y'], 10 - food['x'], 10 - food['y'])
            # 端から2マス以内の餌は危険（追い詰められる可能性）
            if food_wall_dist > 2:
                safe_food_list.append(food)
            # 端から2マス以内でも、敵より十分長い場合は安全
            elif my_length > op_length + 2:
                safe_food_list.append(food)

    # 候補が一つもない場合はNone
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
    # 最短のえさが複数あったら欄d無で返す
    if candidates:
        return random.choice(candidates)
    return None


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
        "head": "bird",  # TODO: Choose head
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

    #敵の次の体を省く（体の長さによって）
    enemy_adjacent_moves = []
    if my_head_u in target_nextbody:
        enemy_adjacent_moves.append("up")
        if my_length <= len(target_body):
            is_move_safe["up"] = False
    if my_head_d in target_nextbody:
        enemy_adjacent_moves.append("down")
        if my_length <= len(target_body):
            is_move_safe["down"] = False
    if my_head_l in target_nextbody:
        enemy_adjacent_moves.append("left")
        if my_length <= len(target_body):
            is_move_safe["left"] = False
    if my_head_r in target_nextbody:
        enemy_adjacent_moves.append("right")
        if my_length <= len(target_body):
            is_move_safe["right"] = False
    # Are there any safe moves left?

    #各方向のture,falseから行けるところのみを抽出
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)


    if len(safe_moves) == 0:
        # 敵の隣しか選択肢がない場合はワンチャンかける
        if len(enemy_adjacent_moves) > 0:
            return {"move": enemy_adjacent_moves[0]}
        return {"move": "down"}

    my_snake = game_state["you"]
    enemy_snake = [s for s in game_state['board']['snakes'] if s['id'] != my_snake['id']][0]


    move_positions = {"up": my_head_u,"down": my_head_d,"left": my_head_l,"right": my_head_r}

    move_scores = {}
    for move in safe_moves:
        pos = move_positions[move]
        safety_score = evaluate_position_safety(pos, game_state, my_snake, enemy_snake)
    
        if is_narrow_path(pos, game_state, my_body, target_body, target_head):
            safety_score -= 500

        if move in enemy_adjacent_moves and my_length > len(target_body):
            can_trap, trap_quality = can_effectively_trap_enemy(
                my_head, my_body, target_head, target_body, enemy_snake, game_state
            )
            if can_trap and trap_quality >= 2:
                safety_score += 50  
            else:
                safety_score -= 20 
        elif move in enemy_adjacent_moves and my_length >= len(target_body):
            can_trap, trap_quality = can_effectively_trap_enemy(
                my_head, my_body, target_head, target_body, enemy_snake, game_state
            )
            if can_trap and trap_quality >= 2:
                safety_score += 30
            else:
                safety_score -= 20  
    
        move_scores[move] = safety_score

    # Choose a random move from the safe ones
    # next_move = random.choice(safe_moves)



    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
    
        if next_move not in safe_moves:
            print(f"Route move {next_move} is not safe, clearing route")
            route_list = []
        elif not is_move_safe.get(next_move, False):
            print(f"Route move {next_move} violates safety rules, clearing route")
            route_list = []
        else:
            next_pos = move_positions[next_move]
            if is_narrow_path(next_pos, game_state, my_body, target_body, target_head):
                print(f"Avoiding narrow path, re-evaluating")
                route_list = []
                if move_scores:
                    next_move = max(move_scores, key=move_scores.get)
                else:
                    next_move = random.choice(safe_moves)
            else:
                reachable = floodfill(next_pos, game_state, my_body, target_body)
                if reachable < my_length:
                    print(f"Warning: Limited reachable area ({reachable} < {my_length}), re-evaluating")
                    route_list = []
                    if move_scores:
                        next_move = max(move_scores, key=move_scores.get)
                    else:
                        next_move = random.choice(safe_moves)

            if len(route_list) >= 0 and next_move in safe_moves and is_move_safe.get(next_move, False):
                print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                print(f"MOVE {game_state['turn']}: {next_move}")
                return {"move": next_move}
            else:
                route_list = []




    #目的ますを決める
    is_trapped, trapped_severity = is_being_trapped(my_head, my_body, target_head, target_body, game_state)
    
    if is_trapped:
        
        food_target = determine_food(game_state)
        if food_target is not None and is_safe_food(food_target, my_head, my_body, target_head, target_body, game_state):
            target = food_target
            print(f"DEFENSIVE: Going for safe food at {target}")
        else:
            if move_scores:
                best_move = max(move_scores, key=move_scores.get)
                print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                print(f"MOVE {game_state['turn']}: Best safe move (trapped) {best_move}")
                return {"move": best_move}
            else:
                print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                print(f"MOVE {game_state['turn']}: Random (trapped, no alternatives)")
                return {"move": random.choice(safe_moves)}
    else:
        can_trap, trap_quality = can_effectively_trap_enemy(my_head, my_body, target_head, target_body, enemy_snake, game_state)
        
        if can_trap and trap_quality >= 2:
            attack_target = plan_attack_strategy(game_state, my_head, my_body, target_head, target_body, enemy_snake)
            if attack_target is not None:
                target = attack_target
                print(f"ATTACK MODE: Targeting {target} (trap quality: {trap_quality})")
            else:
                food_target = determine_food(game_state)
                if food_target is not None and is_safe_food(food_target, my_head, my_body, target_head, target_body, game_state):
                    target = food_target
                    print(f"ATTACK MODE: Going for safe food at {target}")
                else:
                    center = {"x": 5, "y": 5}
                    center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
                    if center_dist > 2:
                        target = center
                    else:
                        if move_scores:
                            best_move = max(move_scores, key=move_scores.get)
                            print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                            print(f"MOVE {game_state['turn']}: Best safe move (no attack opportunity) {best_move}")
                            return {"move": best_move}
                        else:
                            print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                            print(f"MOVE {game_state['turn']}: Random (no attack opportunity)")
                            return {"move": random.choice(safe_moves)}
        else:
            food_target = determine_food(game_state)
            if food_target is not None and is_safe_food(food_target, my_head, my_body, target_head, target_body, game_state):
                target = food_target
                print(f"FOOD MODE: Going for safe food at {target}")
            else:
                center = {"x": 5, "y": 5}
                center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
                if center_dist > 2:
                    target = center
                else:
                    if move_scores:
                        best_move = max(move_scores, key=move_scores.get)
                        print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                        print(f"MOVE {game_state['turn']}: Best safe move (no safe food) {best_move}")
                        return {"move": best_move}
                    else:
                        print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                        print(f"MOVE {game_state['turn']}: Random (no safe food)")
                        return {"move": random.choice(safe_moves)}



        
    obstacle_body = target_body[1:]
    
    route_list = BFS_fastest(game_state, my_body, obstacle_body, 100, [my_head["x"], my_head["y"]], [target["x"], target["y"]])
    print(route_list)

    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
    
        # 基本的な安全性チェック（首の方向などを避ける）
        if next_move not in safe_moves or not is_move_safe.get(next_move, False):
            print(f"Route move {next_move} is unsafe, choosing best alternative")
            if move_scores:
                next_move = max(move_scores, key=move_scores.get)
            else:
                next_move = random.choice(safe_moves)
        else:
            # 経路があっても安全性が極端に低い場合は再評価
            if next_move in move_scores:
                next_move_safety = move_scores[next_move]
                # 他の選択肢と比較
                if move_scores:
                    best_safe_move = max(move_scores, key=move_scores.get)
                    best_safety = move_scores[best_safe_move]
                
                    # 経路の安全性が最良より大幅に低い場合は変更を検討
                    if next_move_safety < best_safety - 100:
                        print(f"Route move {next_move} too dangerous, choosing {best_safe_move}")
                        next_move = best_safe_move
    else:
        if move_scores:
            next_move = max(move_scores, key=move_scores.get)
            
            best_score = move_scores[next_move]
            if best_score < -400:
                for move in safe_moves:
                    pos = move_positions[move]
                    reachable = floodfill(pos, game_state, my_body, target_body)
                    if reachable >= my_length * 0.8:
                        next_move = move
                        break
        elif safe_moves:
            next_move = random.choice(safe_moves)
        else:
            # どうしようもない場合
            next_move = "up"

    print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}
# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})
