import telebot
import time
from config import *
from simple_gpt_yandex import *
from sql import *

bot = telebot.TeleBot(TOKEN)

buf_dict_for_response = {}

def inital_markup_for_commands():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Search for a job🔍', callback_data='search')) # done
    markup.add(telebot.types.InlineKeyboardButton(text='Generate random vacancy🎲', callback_data='vacancy')) # done
    markup.add(telebot.types.InlineKeyboardButton(text='View my saved jobs👀', callback_data='saved')) # done
    markup.add(telebot.types.InlineKeyboardButton(text='Get a random advice for employment😎', callback_data='advice')) # 
    return markup

def save_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Save', callback_data='save'))
    markup.add(telebot.types.InlineKeyboardButton(text='Don\'t save', callback_data='dont_save'))
    return markup

def save_or_dont_save(message):
    # send the markup to the user
    bot.send_message(message.chat.id, 'Do you want to save this vacancy?🤨', reply_markup=save_markup())
    

def job_based_on_preferences(message):
    # send a searching sticker
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAENEG9nJyxRQLzNdNN_7ztnXp1RP151VAACVQADr8ZRGmTn_PAl6RC_NgQ')
    response = random_vacancy(f'generate new vacancy based on user preferences: {message.text}')
    buf_dict_for_response[message.from_user.id] = response
    # delete previous bots message
    bot.delete_message(message.chat.id, message.message_id+1)
    bot.send_message(message.chat.id, response)
    # save or dont save
    save_or_dont_save(message)

def view_saved_vacancies_markup(message):
    id = manager.select_data(f'SELECT id FROM users WHERE telegram_id={message.from_user.id}')[0][0]
    vacancies = manager.select_data(f'SELECT description, name, id FROM vacancies WHERE user_id={id}')
    if len(vacancies) == 0:
        return False

    markup = telebot.types.InlineKeyboardMarkup()
    for i in vacancies:
        markup.add(telebot.types.InlineKeyboardButton(text=f'{i[1]}', callback_data=f'vacancy number {i[2]}'))
    return markup

def setting_name(message):
    #say that the vacancy was saved
    bot.send_message(message.chat.id, 'Your vacancy was saved!🥳')
    # save it to db
    id = manager.select_data(f'SELECT id FROM users WHERE telegram_id={message.from_user.id}')[0][0]
    manager.executemany('INSERT INTO vacancies (user_id, description, name) VALUES (?,?,?)', [(id, buf_dict_for_response[message.from_user.id], message.text)])
    # initial markup for commands
    bot.send_message(message.chat.id, '🟩Choose an option🟩', reply_markup=inital_markup_for_commands())

def delete_or_view(message, id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='DELETE⛔', callback_data=f'delete {id}'))
    markup.add(telebot.types.InlineKeyboardButton(text='VIEW👀', callback_data=f'view {id}'))
    return markup



@bot.message_handler(commands=['start'])
def start_command(message):
    # check if user exists in db
    if message.from_user.id not in buf_dict_for_response.keys():
        buf_dict_for_response[message.from_user.id] = 0
    result = manager.select_data('SELECT telegram_id FROM users', [])
    for i in result:
        if (message.from_user.id == i[0]):
            break
    else:
        manager.executemany('INSERT INTO users (telegram_id, username) VALUES (?,?)', [(message.from_user.id, message.from_user.username)])
        result = manager.select_data('SELECT telegram_id FROM users', [])
    
    bot.send_message(message.chat.id, f'''Hello, @{message.from_user.username}! I am HR Telegram Bot. I will help you find a job based on your preferences.😎
🟩Choose an option🟩''', reply_markup=inital_markup_for_commands())
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    markup = True
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if call.data =='search':
        markup = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Please provide your job preferences, salary, field etc.😁')
        bot.register_next_step_handler(call.message, job_based_on_preferences)
    elif call.data =='saved':
        markup = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # sending markup
        marka = view_saved_vacancies_markup(call)
        if not marka:
            bot.send_message(call.message.chat.id, 'You have no saved vacancies.😭')
            markup = True
        else:
            bot.send_message(call.message.chat.id, '🟩Choose a vacancy to view🟩', reply_markup=view_saved_vacancies_markup(call))
    elif call.data == 'vacancy':
        markup = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Generating a random vacancy for you...')
        # animation of typing
        bot.send_chat_action(call.message.chat.id, 'typing')
        time.sleep(1)
        # generating the vacancy
        response = random_vacancy('generate new vacancy')
        buf_dict_for_response[call.from_user.id] = response
        # sending the vacancy to the user
        bot.send_message(call.message.chat.id, response)
        bot.delete_message(call.message.chat.id, call.message.message_id+1)
        save_or_dont_save(call.message)
    elif call.data == 'save':
        markup = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # set the name for it
        bot.send_message(call.message.chat.id, 'Please set a name for this vacancy.😱')
        bot.register_next_step_handler(call.message, setting_name)
    elif call.data == 'dont_save':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif 'vacancy number' in call.data:
        markup = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # send the delete or view markup
        vacancy_id = int(call.data.split(' ')[-1])
        bot.send_message(call.message.chat.id, '🟩Choose an action🟩', reply_markup=delete_or_view(call, vacancy_id))
    elif 'delete' in call.data:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # get the id of the vacancy
        vacancy_id = int(call.data.split(' ')[-1])
        manager.executemany('DELETE FROM vacancies WHERE id=?', [(vacancy_id,)])
        bot.send_message(call.message.chat.id, 'Vacancy was deleted successfully!🥶')
    elif 'view' in call.data:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # get the id of the vacancy
        vacancy_id = int(call.data.split(' ')[-1])
        vacancy = manager.select_data(f'SELECT description, name FROM vacancies WHERE id={vacancy_id}', [])
        bot.send_message(call.message.chat.id, f'Name: {vacancy[0][1]} \n {vacancy[0][0]}')
    elif call.data == 'advice':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # send an advice using random advice function of advice manager
        bot.send_message(call.message.chat.id, f'{advice_manager.random_advice()}❗')

    if markup:
        bot.send_message(call.message.chat.id, '🟩Choose an option🟩', reply_markup=inital_markup_for_commands())
if __name__ == '__main__':
    manager = User_vacancies_manger(DATABASE)
    advice_manager = Advices_database(ADVICE_DATABASE)
    bot.infinity_polling()