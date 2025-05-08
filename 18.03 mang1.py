import random
import pygame
import sys
import time

# Initialize pygame
pygame.init()

# Set up display
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Fishing Game")

# Load assets
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((135, 206, 250))  # Light blue sky color
font = pygame.font.Font(None, 36)

# Load sounds (with error handling)
try:
    pygame.mixer.init()
    cast_sound = pygame.mixer.Sound("cast.wav")  # Add a cast sound file
    catch_sound = pygame.mixer.Sound("catch.wav")  # Add a catch sound file
    lose_sound = pygame.mixer.Sound("lose.wav")  # Add a lose sound file
except FileNotFoundError:
    print("Warning: Sound files not found. Continuing without sound effects.")
    cast_sound = None
    catch_sound = None
    lose_sound = None

# Fish lists
common_fish = ["Goldfish", "Trout", "Bass", "Salmon", "Catfish", "Tuna", "Bluegill", "Perch", "Carp", "Sunfish",
               "Crappie", "Pike", "Walleye", "Sardine", "Anchovy", "Mackerel", "Herring", "Flounder", "Cod", "Haddock"]
uncommon_fish = ["Rainbow Trout", "Striped Bass", "Channel Catfish", "Yellow Perch", "Brown Trout", "Lake Trout",
                 "White Bass", "Black Crappie", "Blue Catfish", "Flathead Catfish", "Northern Pike", "Muskellunge",
                 "Smallmouth Bass", "Largemouth Bass", "Redfish"]
rare_fish = ["Sturgeon", "Mahi Mahi", "Wahoo", "Snook", "Tarpon", "Barracuda", "Amberjack", "Cobia", "Kingfish",
             "Grouper", "Red Snapper", "Yellowfin Tuna", "Bluefin Tuna", "Swordfish", "Marlin"]
epic_fish = ["Arapaima", "Goliath Tigerfish", "Nile Perch", "Peacock Bass", "Golden Trout", "Arctic Char",
             "Albacore Tuna", "Sailfish", "Blue Marlin", "Black Marlin"]
legendary_fish = ["Coelacanth", "Megamouth Shark", "Goblin Shark", "Oarfish", "Leedsichthys"]

# Combine all fish lists
all_fish = common_fish + uncommon_fish + rare_fish + epic_fish + legendary_fish

# Difficulty settings
difficulty = {
    "common": 3,  # Increased hold time
    "uncommon": 4,
    "rare": 5,
    "epic": 6,
    "legendary": 7
}

# Stamina system
stamina = 100
max_stamina = 100
stamina_regeneration_rate = 0.25  # Halved stamina regeneration rate

# Score system
score = 0
level = 1
level_time = 5 * 60  # 5 minutes per level in seconds
level_score = 300  # Starting score for level 1

# Death messages for each level
death_messages = [
    "Sa püüdsid end ise konksu otsa.",  
"Sa heitsid õnge välja, kuid libisesid ja surid.",  
"Lind lõi su pead sisse.",  
"Sa proovisid kala ja saad mürgistusse.",  
"Linnavalve võttis su kinni ja hukkas.",  
"Su tabas koolera.",  
"Kala tõmbas su vette.",  
"Veekogust hüppas välja krokodill.",  
"Konkurendid elimineerisid su.",  
"Sa läksid toiduga kinni."
]

def draw_text(text, x, y, color=(0, 0, 0)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_stamina_bar():
    bar_width = 200
    bar_height = 20
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH // 2 - bar_width // 2, HEIGHT - 50, bar_width, bar_height))
    if stamina < 30:
        color = (255, 255, 0)  # Yellow for low stamina
    else:
        color = (0, 255, 0)  # Green for normal stamina
    pygame.draw.rect(screen, color, (WIDTH // 2 - bar_width // 2, HEIGHT - 50, bar_width * (stamina / max_stamina), bar_height))

def draw_progress_bar(progress):
    bar_width = 200
    bar_height = 20
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH // 2 - bar_width // 2, HEIGHT - 100, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 0, 255), (WIDTH // 2 - bar_width // 2, HEIGHT - 100, bar_width * progress, bar_height))
    draw_text(f"{int(progress * 100)}%", WIDTH // 2 - 20, HEIGHT - 130)

def get_fish_rarity(fish):
    if fish in common_fish:
        return "Common"
    elif fish in uncommon_fish:
        return "Uncommon"
    elif fish in rare_fish:
        return "Rare"
    elif fish in epic_fish:
        return "Epic"
    elif fish in legendary_fish:
        return "Legendary"
    return "Unknown"

def get_fish_score(fish):
    if fish in common_fish:
        return 10
    elif fish in uncommon_fish:
        return 20
    elif fish in rare_fish:
        return 50
    elif fish in epic_fish:
        return 100
    elif fish in legendary_fish:
        return 200
    return 0

def get_fish_list(level):
    # Adjust fish probabilities based on level
    if level <= 3:
        return common_fish + uncommon_fish * 2 + rare_fish + epic_fish + legendary_fish
    elif level <= 6:
        return common_fish + uncommon_fish + rare_fish * 2 + epic_fish + legendary_fish
    elif level <= 9:
        return uncommon_fish + rare_fish + epic_fish * 2 + legendary_fish
    else:
        return rare_fish + epic_fish + legendary_fish * 2

def fishing_minigame(fish):
    global stamina
    bar_width, bar_height = WIDTH // 4, 30
    bar_x, bar_y = (WIDTH - bar_width) // 2, HEIGHT // 2
    green_width = bar_width // 5
    green_x = bar_x  # Start at the left edge
    fish_x = bar_x + bar_width // 2 - 10
    fish_speed = 2  # Скорость удочки (синий бар)

    # Скорость рыбы (зелёный бар) уменьшена на четверть
    green_speed = random.uniform(0.75, 1.875)  # Было random.uniform(1, 2.5), теперь на 25% медленнее

    # Determine hold time based on fish rarity
    if fish in common_fish:
        hold_time = difficulty["common"]
    elif fish in uncommon_fish:
        hold_time = difficulty["uncommon"]
    elif fish in rare_fish:
        hold_time = difficulty["rare"]
    elif fish in epic_fish:
        hold_time = difficulty["epic"]
    else:
        hold_time = difficulty["legendary"]

    caught = False
    time_inside = 0
    green_direction = 1
    timer = 11 * 60  # Increased timer by 1 second (11 seconds at 60 FPS)

    while timer > 0:
        screen.blit(background, (0, 0))
        draw_text("Keep the fish inside the green zone!", WIDTH // 3, HEIGHT // 3)
        draw_text("Move left: A | Move right: D", WIDTH // 3, HEIGHT // 3 + 40)  # Добавлено описание управления
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (green_x, bar_y, green_width, bar_height))

        # Ограничение движения синего индикатора
        fish_x = max(bar_x, min(bar_x + bar_width - 20, fish_x))  # Не выходит за пределы бара
        pygame.draw.rect(screen, (0, 0, 255), (fish_x, bar_y, 20, bar_height))

        draw_stamina_bar()

        # Draw progress bar
        progress = min(1.0, time_inside / (hold_time * 60))
        draw_progress_bar(progress)

        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            fish_x -= fish_speed
            stamina -= 0.05  # Halved stamina depletion rate
        if keys[pygame.K_d]:
            fish_x += fish_speed
            stamina -= 0.05  # Halved stamina depletion rate

        # Regenerate stamina when not reeling
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            stamina = min(max_stamina, stamina + stamina_regeneration_rate)

        green_x += green_direction * green_speed
        if green_x <= bar_x or green_x + green_width >= bar_x + bar_width:
            green_direction *= -1  # Reverse direction when hitting the edges
            green_speed = random.uniform(0.75, 1.875)  # Обновляем скорость зелёного бара

        if green_x <= fish_x <= green_x + green_width:
            time_inside += 1
        else:
            time_inside = 0

        if time_inside >= hold_time * 60:  # Increased hold time (60 frames per second)
            caught = True
            return caught

        if stamina <= 0:
            return False

        timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    return False  # Timer ran out

def show_story(player_name):
    screen.blit(background, (0, 0))
    draw_text(f"{player_name}, valitseb kuningas Arnoldus.", 20, 20)
    draw_text("Tema nimi oled vaesest perest pärit.", 20, 60)
    draw_text("Koleera võttis sinu isa ja ema ära, sa oled nüüd üksinda.", 20, 100)
    draw_text("Sul on toitu vaid paariks päevaks.", 20, 140)
    draw_text("Sinu isa õpetas sind, kuidas kala püüda.", 20, 180)
    draw_text("Sul pole õngeridva, seega pead selle leidma, et ellu jääda.", 20, 220)
    draw_text("Sinu ees on kaks teed: kas metsa või linna.", 20, 260)
    draw_text("Vali metsa (M) või linna (L).", 20, 300)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "metsa"
                elif event.key == pygame.K_l:
                    return "linna"

def handle_choice(choice, player_name):
    screen.blit(background, (0, 0))
    if choice == "metsa":
        draw_text(f"{player_name}, sa läksid metsa.", 20, 20)
        draw_text("Sa läbisid põõsastikku ja kaotasid kogu oma toidu.", 20, 60)
        draw_text("Kuid sa leidsid pika kepi.", 20, 100)
        draw_text("Sa naasid ema laiba juurde ja võtsid tema juuksest nööri.", 20, 140)
        draw_text("Sa tegid õngeridva ja läksid kalale.", 20, 180)
    elif choice == "linna":
        draw_text(f"{player_name}, sa läksid linna.", 20, 20)
        draw_text("Sa vahetasid oma saapad kalamehega õngeridva vastu.", 20, 60)
        draw_text("Nüüd saad minna kalale.", 20, 100)
    pygame.display.flip()
    pygame.time.delay(5000)  # Show the result for 5 seconds

def fishing_game():
    global stamina, score, level, level_score
    caught_fish = []
    running = True
    game_started = False
    player_name = ""

    # Main menu
    while not game_started:
        screen.blit(background, (0, 0))
        draw_text("Fishing Game", WIDTH // 2 - 70, HEIGHT // 2 - 50, (0, 0, 0))
        draw_text("Press P to Play", WIDTH // 2 - 90, HEIGHT // 2, (0, 0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_started = True

    # Enter player name
    screen.blit(background, (0, 0))
    draw_text("Enter your name:", 20, 20)
    pygame.display.flip()

    name_entered = False
    while not name_entered:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name_entered = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode
                screen.blit(background, (0, 0))
                draw_text("Enter your name:", 20, 20)
                draw_text(player_name, 20, 60)
                pygame.display.flip()

    # Show story
    choice = show_story(player_name)
    handle_choice(choice, player_name)

    # Main game loop
    while running:
        start_time = time.time()
        while time.time() - start_time < level_time:
            screen.blit(background, (0, 0))
            draw_text(f"Level: {level}", 20, 20)
            draw_text(f"Score to reach: {level_score}", 20, 60)
            draw_text("Caught Fish:", 20, 100)
            for i, fish in enumerate(caught_fish):
                rarity = get_fish_rarity(fish)
                draw_text(f"- {fish} ({rarity})", 20, 140 + i * 30)
            draw_text(f"Score: {score}", 20, HEIGHT - 50)
            draw_text("Press SPACE to cast your line.", 20, HEIGHT - 100)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if cast_sound:
                            cast_sound.play()
                        stamina = max_stamina  # Reset stamina
                        fish = random.choice(get_fish_list(level))  # Выбор рыбы с учётом уровня
                        if fishing_minigame(fish):
                            if catch_sound:
                                catch_sound.play()
                            caught_fish.append(fish)
                            score += get_fish_score(fish)
                            rarity = get_fish_rarity(fish)
                            message = f"You caught a {fish} ({rarity})!"
                        else:
                            if lose_sound:
                                lose_sound.play()
                            message = "The fish got away!"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        break

            if score >= level_score:
                level += 1
                level_score += 100  # Increase score requirement by 100
                if level > 10:
                    screen.blit(background, (0, 0))
                    draw_text("Congratulations!", WIDTH // 2 - 100, HEIGHT // 2 - 50)
                    draw_text("You have completed all 10 levels!", WIDTH // 2 - 150, HEIGHT // 2)
                    draw_text("You caught enough fish to sell and rent a house!", WIDTH // 2 - 200, HEIGHT // 2 + 50)
                    pygame.display.flip()
                    pygame.time.delay(5000)
                    running = False
                    break
                else:
                    screen.blit(background, (0, 0))
                    draw_text(f"Level {level} completed!", WIDTH // 2 - 100, HEIGHT // 2 - 50)
                    draw_text(f"Score to reach: {level_score}", WIDTH // 2 - 100, HEIGHT // 2)
                    pygame.display.flip()
                    pygame.time.delay(3000)
                    break
        else:
            # Time ran out, player failed the level
            screen.blit(background, (0, 0))
            draw_text(f"Level {level} failed!", WIDTH // 2 - 100, HEIGHT // 2 - 50)
            draw_text(death_messages[level - 1], WIDTH // 2 - 200, HEIGHT // 2)
            pygame.display.flip()
            pygame.time.delay(5000)
            running = False

    pygame.quit()

if __name__ == "__main__":
    try:
        fishing_game()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

PEENIS

