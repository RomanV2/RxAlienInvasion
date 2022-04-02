import sys
import pygame

from time import sleep

from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """
    реагирует на нажатие клавиш
    """
    if event.key == pygame.K_RIGHT:
        # переместить корабль вправо
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        # переместить корабль влево
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        # создание пули и включение ее в группу
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        # переместить корабль вправо
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        # переместить корабль вправо
        ship.moving_left = False


def check_play_button(ai_settings, screen, stats, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    """
    запускает игру при нажатии кнопки
    """
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # сброс игровых настроек
        ai_settings.initialize_dynamic_settings()
        # скрытие курсора
        pygame.mouse.set_visible(False)
        # сброс игровой статистики
        stats.reset_stats()
        stats.game_active = True
        # очистка списка нло и пуль
        aliens.empty()
        bullets.empty()
        # создание нового флота и центрирование корабля
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

def check_events(ai_settings, screen, stats, play_button, ship, aliens, bullets):
    """
    Обрабатывает нажатие клавиш и мыши
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, play_button, ship, aliens, bullets, mouse_x, mouse_y)



def update_screen(ai_settings, screen, stats, ship, aliens, bullets, play_button):
    """
    Обновляет изображения на экране и отображает новый экран
    """
    # перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # все пули выводятся позади изображения корабля и пришельцев
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    # отображает кнопку, если игра неактивна
    if not stats.game_active:
        play_button.draw_button()

    # отображение последнего прорисованного экрана
    pygame.display.flip()


def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets):
    """
    обработка коллизий пуль с нло
    """
    # проверка попадания
    # при попадании удалить пулю и нло
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if len(aliens) == 0:
        # уничтожает все пули, увеличивает скорсть игры и создает флот нло
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)


def update_bullets(ai_settings, screen, ship, aliens, bullets):
    """
    обновляет позиции пуль и удаляет старые
    """
    bullets.update()
    # удаление пуль за экраном
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets)


def fire_bullet(ai_settings, screen, ship, bullets):
    """
    выпускает пулю, если максимум еще не достигнут
    """
    # создание пули и включениее ее в группу
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def get_number_aliens_x(ai_settings, alien_width):
    """
    вычисляет кличество нло в ряду
    """
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """
    определяет количесво рядов нло
    """
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """
    создает нло и размещает в ряду
    """
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """
    создает флот нло
    """
    # создание нло и вычисление их количества в ряду
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # создание флота нло
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            # создание и размещение нло в ряду
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def change_fleet_directions(ai_settings, aliens):
    """
    опускает весь флот и меняет направление
    """
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_fleet_edges(ai_settings, aliens):
    """
    реагиреут на достижение нло края экрана
    """
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_directions(ai_settings, aliens)
            break


def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets):
    """
    проверяет касаниее нло низа экрана
    """
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # тоже самое что и при касание нло карабля
            ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
    """
    проверяет край и обновляет позиции всех НЛО во флоте
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    # проверяет коллизии нло корабль
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
    # проверка достжения нло до низа экрана
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets)


def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
    """
    обрабатывает столкновение корабля с нло
    """
    if stats.ships_left > 0:
        # уменьшает ship_left
        stats.ships_left -= 1

        # очистка нло и пуль
        aliens.empty()
        bullets.empty()

        # создание нового корабля и флота нло
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # пауза
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

