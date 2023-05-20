command_start = '/stats'
only_for_admins = 'Sorry, this function is available only for admins. Set "admin" flag in django admin panel.'
only_for_admins_ru = 'Извините, но эта функция доступна только администраторам. По вопросам присвоения статуса обратитесь к администрации.'

secret_admin_commands = f"⚠️ Secret Admin commands\n" \
                        f"{command_start} - bot stats"

users_amount_stat = "<b>Users</b>: {user_count}\n" \
                    "<b>24h active</b>: {active_24}"

welcome_message = f"Добро пожаловать!\n\n Для начала работы нажмите на кнопку '/start' или ввидите команду вручную."
