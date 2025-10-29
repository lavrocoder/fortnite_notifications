import plyer


def send_win_notification(message):
    plyer.notification.notify(
        message=message,
        title='Уведомление для Fortnite'
    )



if __name__ == '__main__':
    send_win_notification('Проверь магазин')
