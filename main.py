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
    """
    指定位置から到達可能なマス数をカウント（安全性評価用）
    """
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
    """
    位置の安全性を数値で評価（高いほど安全）
    """
    score = 0
    my_body = my_snake['body']
    enemy_body = enemy_snake['body']
    enemy_head = enemy_snake['head']
    my_length = my_snake['length']
    enemy_length = enemy_snake['length']
    
    # 1. Floodfill：到達可能領域（最重要）
    reachable = floodfill(pos, game_state, my_body, enemy_body)
    score += reachable * 10
    
    # 2. 中央への近さ（11x11なので中心は5,5）
    center_dist = abs(pos['x'] - 5) + abs(pos['y'] - 5)
    score += (10 - center_dist) * 3
    
    # 3. 敵の頭との距離（長さによって評価が変わる）
    enemy_dist = abs(pos['x'] - enemy_head['x']) + abs(pos['y'] - enemy_head['y'])
    length_diff = my_length - enemy_length
    
    if length_diff > 0:
        # 相手より長い：中央制圧を優先しつつ、敵との距離も考慮
        # 敵より中央に近い位置にボーナス
        my_center_dist = abs(pos['x'] - 5) + abs(pos['y'] - 5)
        enemy_center_dist = abs(enemy_head['x'] - 5) + abs(enemy_head['y'] - 5)
        
        if my_center_dist < enemy_center_dist:
            # 自分の方が中央に近い = 良い配置
            score += 50
        
        # 敵に近すぎず遠すぎない距離を維持（3-5マス程度）
        if 3 <= enemy_dist <= 5:
            score += 30
        elif enemy_dist < 3:
            score += 10  # 近すぎるとリスク
        elif enemy_dist > 7:
            score -= 20  # 遠すぎると圧力がかからない
    else:
        # 相手より短い：敵から遠い方が良い（防御的）
        score += enemy_dist * 3
    
    # 4. 壁への近さペナルティ
    wall_dist = min(pos['x'], pos['y'], 10 - pos['x'], 10 - pos['y'])
    score += wall_dist * 2
    
    return score

def is_narrow_path(pos, game_state, my_body, enemy_body, enemy_head):
    """
    幅1の危険な経路かどうかを判定
    敵が動くことで塞がれる可能性も考慮
    """
    my_length = len(my_body)
    
    # その位置からの到達可能領域が少ない場合
    reachable = floodfill(pos, game_state, my_body, enemy_body)
    
    # 自分の体長より到達可能領域が少ない場合は危険
    if reachable < my_length:
        return True
    
    # 到達可能領域が体長の2倍以下なら危険
    if reachable < my_length * 2:
        return True

    # 到達可能領域が15マス以下も危険
    if reachable < 15:
        return True
    
    # ★★★ 追加：敵が1手動いた後の空間もチェック ★★★
    # 敵の頭の隣接マス（敵が次に移動できる場所）
    enemy_next_positions = [
        {'x': enemy_head['x'], 'y': enemy_head['y'] + 1},
        {'x': enemy_head['x'], 'y': enemy_head['y'] - 1},
        {'x': enemy_head['x'] - 1, 'y': enemy_head['y']},
        {'x': enemy_head['x'] + 1, 'y': enemy_head['y']}
    ]
    
    # 敵が各方向に動いた場合をシミュレート
    min_reachable_after_enemy_move = reachable
    for enemy_next_pos in enemy_next_positions:
        # 範囲外チェック
        if not (0 <= enemy_next_pos['x'] < 11 and 0 <= enemy_next_pos['y'] < 11):
            continue
        
        # 敵の体や自分の体と重なる移動は除外
        if enemy_next_pos in enemy_body or enemy_next_pos in my_body:
            continue
        
        # 敵が1マス動いた後の体を作成（尾が1マス短くなる想定）
        simulated_enemy_body = [enemy_next_pos] + enemy_body[:-1]
        
        # その状態でposから到達可能な領域を計算
        reachable_after = floodfill(pos, game_state, my_body, simulated_enemy_body)
        min_reachable_after_enemy_move = min(min_reachable_after_enemy_move, reachable_after)
    
    # 敵が動いた後の最悪ケースで体長以下なら危険
    if min_reachable_after_enemy_move < my_length:
        print(f"Narrow path detected: reachable drops to {min_reachable_after_enemy_move} after enemy moves")
        return True
    
    # 敵が動いた後の最悪ケースで体長の1.5倍以下なら危険
    if min_reachable_after_enemy_move < my_length * 1.5:
        print(f"Narrow path warning: reachable drops to {min_reachable_after_enemy_move} after enemy moves")
        return True
    
    # 敵の頭が近く、塞がれる可能性がある場合
    enemy_dist = abs(pos['x'] - enemy_head['x']) + abs(pos['y'] - enemy_head['y'])
    if enemy_dist <= 2 and reachable < 20:
        return True
    
    return False

def find_enemy_narrow_corridor(enemy_head, enemy_body, my_body, game_state):
    """
    敵が幅1の経路にいるかを判定し、いる場合はその経路情報を返す
    """
    # 敵の位置から到達可能な領域を調べる
    reachable = floodfill(enemy_head, game_state, enemy_body, my_body)
    
    # 到達可能領域が少ない = 幅1経路にいる可能性
    if reachable < 8:
        # 経路の出口を探す
        exits = find_corridor_exits(enemy_head, enemy_body, my_body, game_state)
        if len(exits) > 0:
            return {
                'in_corridor': True,
                'exits': exits,
                'reachable_area': reachable
            }
    
    return None


def find_corridor_exits(start_pos, enemy_body, my_body, game_state):
    """
    幅1経路の出口（広い空間への入り口）を見つける
    """
    exits = []
    visited = set()
    queue = [(start_pos['x'], start_pos['y'])]
    visited.add((start_pos['x'], start_pos['y']))
    
    while queue:
        x, y = queue.pop(0)
        pos = {'x': x, 'y': y}
        
        # この位置からの到達可能領域を確認
        local_reachable = floodfill(pos, game_state, enemy_body, my_body)
        
        # 急に広くなる場所 = 出口
        if local_reachable > 15:
            exits.append(pos)
            continue  # この先は探索しない
        
        # 隣接マスを探索
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
    """
    出口を塞ぐための最適な位置を計算
    """
    if not exits:
        return None
    
    # 最も近い出口を選ぶ
    closest_exit = min(exits, key=lambda e: abs(my_head['x'] - e['x']) + abs(my_head['y'] - e['y']))
    
    # 出口の隣接マス（実際に塞ぐ位置）を返す
    return closest_exit


def detect_wall_herding_opportunity(enemy_head, enemy_body, my_head, my_body, game_state):
    """
    敵が端に寄っているかを検出し、並走で追い込めるかを判定
    """
    # 敵の壁への近さ
    enemy_wall_dist = min(enemy_head['x'], enemy_head['y'], 
                          10 - enemy_head['x'], 10 - enemy_head['y'])
    
    # 敵が端に寄っているか、または端方向に移動中か判定
    # より早い段階で並走を開始するため、条件を緩和（4マスまで）
    if enemy_wall_dist > 4:
        return None  # まだ端に向かっていない
    
    # 敵がどの端に寄っているか判定
    edge_type = None
    parallel_line = None  # ä¸¦èµ°ã™ã‚‹ãƒ©ã‚¤ãƒ³
    
    if enemy_head['x'] <= 2:
        edge_type = 'left'
        parallel_line = 3  # X=3ã®ãƒ©ã‚¤ãƒ³ã§åˆ†æ–­
    elif enemy_head['x'] >= 8:
        edge_type = 'right'
        parallel_line = 7  # X=7ã®ãƒ©ã‚¤ãƒ³ã§åˆ†æ–­
    elif enemy_head['y'] <= 2:
        edge_type = 'bottom'
        parallel_line = 3  # Y=3ã®ãƒ©ã‚¤ãƒ³ã§åˆ†æ–­
    elif enemy_head['y'] >= 8:
        edge_type = 'top'
        parallel_line = 7  # Y=7ã®ãƒ©ã‚¤ãƒ³ã§åˆ†æ–­
    else:
        return None
    
    # è‡ªåˆ†ãŒæ—¢ã«åˆ†æ–­ãƒ©ã‚¤ãƒ³ã‚ˆã‚Šä¸­å¤®å¯„ã‚Šã«ã„ã‚‹ã‹ç¢ºèª
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
    
    # ★★★ ここから追加 ★★★
    # 分断ラインを作った場合の自分側と敵側の空間を評価
    my_safe_space = 0
    enemy_trapped_space = 0
    
    if edge_type == 'left':
        # 敵は左側（X < parallel_line）、自分は右側（X >= parallel_line）
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
    
    # 自分側の空間が十分でない場合は追い込みを中止
    my_length = len(my_body)
    if my_safe_space < my_length + 10:
        print(f"Herding aborted: insufficient safe space ({my_safe_space} < {my_length + 10})")
        return None
    
    # 敵側の空間が狭くなければ効果が薄い
    enemy_length = len(enemy_body)
    if enemy_trapped_space > enemy_length + 10:
        print(f"Herding not effective: enemy has too much space ({enemy_trapped_space})")
        return None
    # ★★★ ここまで追加 ★★★
    
    return {
        'type': 'wall_herding',
        'edge_type': edge_type,
        'parallel_line': parallel_line,
        'is_positioned': is_positioned,
        'enemy_wall_dist': enemy_wall_dist,
        'my_safe_space': my_safe_space,  # 追加
        'enemy_trapped_space': enemy_trapped_space  # 追加
    }


def calculate_parallel_chase_position(my_head, enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state):
    if edge_type == 'left':
        # Enemy at left edge: Position on X=parallel_line with same Y as enemy
        target_x = parallel_line
        target_y = enemy_head['y']
        
        # If already at dividing line, adjust to enemy's Y coordinate
        if my_head['x'] >= parallel_line:
            # More aggressive: aim for enemy's exact Y coordinate
            if abs(my_head['y'] - enemy_head['y']) > 0:
                # Move 1 step closer to enemy's Y
                if my_head['y'] < enemy_head['y']:
                    target_y = my_head['y'] + 1
                else:
                    target_y = my_head['y'] - 1
            else:
                # Already at same Y, maintain position
                target_y = enemy_head['y']
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'right':
        # Enemy at right edge: Position on X=parallel_line with same Y as enemy
        target_x = parallel_line
        target_y = enemy_head['y']
        
        # If already at dividing line, adjust to enemy's Y coordinate
        if my_head['x'] <= parallel_line:
            # More aggressive: aim for enemy's exact Y coordinate
            if abs(my_head['y'] - enemy_head['y']) > 0:
                # Move 1 step closer to enemy's Y
                if my_head['y'] < enemy_head['y']:
                    target_y = my_head['y'] + 1
                else:
                    target_y = my_head['y'] - 1
            else:
                # Already at same Y, maintain position
                target_y = enemy_head['y']
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'bottom':
        # Enemy at bottom edge: Position on Y=parallel_line with same X as enemy
        target_x = enemy_head['x']
        target_y = parallel_line
        
        # If already at dividing line, adjust to enemy's X coordinate
        if my_head['y'] >= parallel_line:
            # More aggressive: aim for enemy's exact X coordinate
            if abs(my_head['x'] - enemy_head['x']) > 0:
                # Move 1 step closer to enemy's X
                if my_head['x'] < enemy_head['x']:
                    target_x = my_head['x'] + 1
                else:
                    target_x = my_head['x'] - 1
            else:
                # Already at same X, maintain position
                target_x = enemy_head['x']
        
        return {'x': target_x, 'y': target_y}
        
    elif edge_type == 'top':
        # Enemy at top edge: Position on Y=parallel_line with same X as enemy
        target_x = enemy_head['x']
        target_y = parallel_line
        
        # If already at dividing line, adjust to enemy's X coordinate
        if my_head['y'] <= parallel_line:
            # More aggressive: aim for enemy's exact X coordinate
            if abs(my_head['x'] - enemy_head['x']) > 0:
                # Move 1 step closer to enemy's X
                if my_head['x'] < enemy_head['x']:
                    target_x = my_head['x'] + 1
                else:
                    target_x = my_head['x'] - 1
            else:
                # Already at same X, maintain position
                target_x = enemy_head['x']
        
        return {'x': target_x, 'y': target_y}
    
    return None
    
    return None


def plan_attack_strategy(game_state, my_head, my_body, enemy_head, enemy_body, enemy_snake):
    """
    攻撃戦略を計画し、目標位置を返す
    優先順位：
    1. 敵が幅1経路にいる → 出口を塞ぐ
    2. 敵が端に寄っている → 並走して追い込む
    3. その他 → 安全性を最優先に中央を維持
    """
    
    # 戦略1: 敵が幅1経路にいるか確認
    corridor_info = find_enemy_narrow_corridor(enemy_head, enemy_body, my_body, game_state)
    if corridor_info and corridor_info['in_corridor']:
        # 出口を塞ぎに行く
        blocking_pos = calculate_blocking_position(my_head, corridor_info['exits'])
        if blocking_pos:
            print(f"STRATEGY: Blocking corridor exit at {blocking_pos}")
            return blocking_pos
        
    
    # 戦略2: 敵を端に追い込めるか確認
    herding_opportunity = detect_wall_herding_opportunity(enemy_head, enemy_body, my_head, my_body, game_state)
    if herding_opportunity:
        edge_type = herding_opportunity['edge_type']
        parallel_line = herding_opportunity['parallel_line']
        is_positioned = herding_opportunity['is_positioned']
        my_safe_space = herding_opportunity.get('my_safe_space', 0)
        enemy_trapped_space = herding_opportunity.get('enemy_trapped_space', 999)
        
        print(f"STRATEGY: Herding enemy at {edge_type} edge, positioned: {is_positioned}")
        print(f"Space check - My side: {my_safe_space}, Enemy side: {enemy_trapped_space}")
        
        # 自分の空間が不十分なら追い込みを中止
        if my_safe_space < len(my_body) + 10:
            print(f"ABORT: My safe space too small, returning to normal strategy")
            return None
        
        # フェーズ1: 分断ラインまでの移動（中央陣取りの位置）
        if not is_positioned:
            # まだ分断ラインに到達していない → 分断ライン上の、敵に近い位置を目指す
            if edge_type in ['left', 'right']:
                # 縦線で分断
                target = {'x': parallel_line, 'y': enemy_head['y']}
            else:
                # 横線で分断
                target = {'x': enemy_head['x'], 'y': parallel_line}
            
            print(f"STRATEGY Phase 1: Moving to dividing line {target}")
            return target
        
        # フェーズ2: 分断ラインに到達済み → 並走して追い込む
        parallel_pos = calculate_parallel_chase_position(
            my_head, enemy_head, enemy_body, my_body, edge_type, parallel_line, game_state
        )
        if parallel_pos:
            print(f"STRATEGY Phase 2: Parallel chase to {parallel_pos}")
            return parallel_pos
        
    # ★★★ ここから追加 ★★★
    # Strategy 3: If longer, push enemy toward edge by controlling center
    my_length = len(my_body)
    enemy_length = len(enemy_body)
    
    if my_length > enemy_length + 1:  # 2マス以上長い場合
        # 敵がどの端に近いか判定
        enemy_distances = {
            'left': enemy_head['x'],
            'right': 10 - enemy_head['x'],
            'bottom': enemy_head['y'],
            'top': 10 - enemy_head['y']
        }
        
        # 最も近い端を特定
        nearest_edge = min(enemy_distances.items(), key=lambda x: x[1])
        edge_name = nearest_edge[0]
        edge_dist = nearest_edge[1]
        
        # 敵が既にある程度端に寄っている場合（5マス以内）
        if edge_dist <= 5:
            # その端方向に敵を押し込むための位置を計算
            if edge_name == 'left':
                # 左端：自分は敵の右側（X方向で大きい位置）で中央寄りに
                push_target = {'x': min(enemy_head['x'] + 3, 7), 'y': enemy_head['y']}
            elif edge_name == 'right':
                # 右端：自分は敵の左側で中央寄りに
                push_target = {'x': max(enemy_head['x'] - 3, 3), 'y': enemy_head['y']}
            elif edge_name == 'bottom':
                # 下端：自分は敵の上側で中央寄りに
                push_target = {'x': enemy_head['x'], 'y': min(enemy_head['y'] + 3, 7)}
            elif edge_name == 'top':
                # 上端：自分は敵の下側で中央寄りに
                push_target = {'x': enemy_head['x'], 'y': max(enemy_head['y'] - 3, 3)}
            
            # 安全性チェック
            push_space = floodfill(push_target, game_state, my_body, enemy_body)
            if push_space >= my_length:
                print(f"STRATEGY: Pushing enemy to {edge_name} edge, target {push_target}")
                return push_target
    # ★★★ ここまで追加 ★★★
    




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
        if my_length <= len(target_body):  # 同じ長さか短い時は基本避ける
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

    #詰んでたらしかたない - ただし敵の隣も考慮
    if len(safe_moves) == 0:
        # 敵の隣しか選択肢がない場合はワンチャンかける
        if len(enemy_adjacent_moves) > 0:
            print(f"MOVE {game_state['turn']}: No choice but enemy adjacent!")
            return {"move": enemy_adjacent_moves[0]}
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # 敵のスネーク情報を取得
    my_snake = game_state["you"]
    enemy_snake = [s for s in game_state['board']['snakes'] if s['id'] != my_snake['id']][0]

    # 各移動の安全性を評価
    move_positions = {"up": my_head_u,"down": my_head_d,"left": my_head_l,"right": my_head_r}

    move_scores = {}
    for move in safe_moves:
        pos = move_positions[move]
        safety_score = evaluate_position_safety(pos, game_state, my_snake, enemy_snake)
    
        # 幅1経路のペナルティ
        if is_narrow_path(pos, game_state, my_body, target_body, target_head):
            safety_score -= 500
    
        # 相手より長い時、敵の隣はボーナス（攻撃的）
        if move in enemy_adjacent_moves and my_length > len(target_body):
            safety_score += 30
    
        move_scores[move] = safety_score

    # Choose a random move from the safe ones
    # next_move = random.choice(safe_moves)



    if(len(route_list) > 0):
        next_move = route_list[0]
        route_list.pop(0)
    
        # まず基本的な安全性をチェック（首の方向などを避ける）
        if next_move not in safe_moves:
            print(f"Route move {next_move} is not safe, clearing route")
            route_list = []
        elif not is_move_safe.get(next_move, False):
            print(f"Route move {next_move} violates safety rules, clearing route")
            route_list = []
        else:
            # 経路上の次の手が幅1経路に入らないかチェック
            next_pos = move_positions[next_move]
            if is_narrow_path(next_pos, game_state, my_body, target_body, target_head):
                # 幅1経路は基本的に避ける
                print(f"Avoiding narrow path, re-evaluating")
                route_list = []
                # 安全な方向を選択
                if move_scores:
                    next_move = max(move_scores, key=move_scores.get)
                else:
                    next_move = random.choice(safe_moves)
            else:
                # 幅1でなくても、到達可能領域が体長より少ない場合は警告
                reachable = floodfill(next_pos, game_state, my_body, target_body)
                if reachable < my_length:
                    print(f"Warning: Limited reachable area ({reachable} < {my_length}), re-evaluating")
                    route_list = []
                    if move_scores:
                        next_move = max(move_scores, key=move_scores.get)
                    else:
                        next_move = random.choice(safe_moves)
        
            # route_listが有効なら実行
            if len(route_list) >= 0 and next_move in safe_moves and is_move_safe.get(next_move, False):
                print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                print(f"MOVE {game_state['turn']}: {next_move}")
                return {"move": next_move}
            else:
                route_list = []




    #目的ますを決める
    if len(target_body) + 2 < len(my_body):
        # 敵より長い時：戦略的攻撃
        attack_target = plan_attack_strategy(game_state, my_head, my_body, target_head, target_body, enemy_snake)
        if attack_target is not None:
            target = attack_target
        else:
            # 攻撃チャンスがない場合は安全な餌取り
            target = determine_food(game_state)
            if target is None:
                # 餌がない場合は中央へ、または最も安全な方向へ
                center = {"x": 5, "y": 5}
                center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
                if center_dist > 2:
                    target = center  # 中央から遠い場合は中央へ
                else:
                    # 中央付近なら最も安全な方向を選んで即座に移動
                    if move_scores:
                        best_move = max(move_scores, key=move_scores.get)
                        print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                        print(f"MOVE {game_state['turn']}: Best safe move (no food, at center) {best_move}")
                        return {"move": best_move}
                    else:
                        print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                        print(f"MOVE {game_state['turn']}: Random (no food, no scores)")
                        return {"move": random.choice(safe_moves)}
    else:
        # エサ取り優先
        target = determine_food(game_state)
        if target is None: # 餌が見つからない場合
            center = {"x": 5, "y": 5}
            center_dist = abs(my_head['x'] - 5) + abs(my_head['y'] - 5)
            if center_dist > 2:
                target = center
            else:
                # 中央付近なら安全な方向へ
                if move_scores:
                    best_move = max(move_scores, key=move_scores.get)
                    print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                    print(f"MOVE {game_state['turn']}: Best safe move (no food) {best_move}")
                    return {"move": best_move}
                else:
                    print(is_move_safe["up"],is_move_safe["down"],is_move_safe["left"],is_move_safe["right"])
                    print(f"MOVE {game_state['turn']}: Random (no alternatives)")
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
        # 経路がない場合は最も安全な方向を選ぶ
        if move_scores:
            next_move = max(move_scores, key=move_scores.get)
            
            # ★ 最後の手段チェック ★
            best_score = move_scores[next_move]
            if best_score < -400:  # Narrow pathペナルティは-500
                print(f"WARNING: Best move {next_move} has low score {best_score}")
                # 体長の80%以上のスペースがある選択肢を探す
                for move in safe_moves:
                    pos = move_positions[move]
                    reachable = floodfill(pos, game_state, my_body, target_body)
                    if reachable >= my_length * 0.8:
                        print(f"FALLBACK: Choosing {move} with reachable {reachable}")
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
