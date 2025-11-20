from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telethon import TelegramClient
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError, PeerIdInvalidError
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_IDS
from database import Database
import asyncio
import re
import random
import string

class MovieBot:
    def __init__(self):
        self.db = Database()
        self.client = TelegramClient('session', API_ID, API_HASH)
        self.setup_client()
    
    def setup_client(self):
        """Setup Telethon client for subscription checking"""
        try:
            self.client.start()
        except Exception as e:
            print(f"Error starting Telethon client: {e}")
    
    async def check_subscription(self, user_id):
        """Check if user is subscribed to the channel with proper error handling"""
        try:
            # Convert channel ID to proper format
            if CHANNEL_ID.startswith('@'):
                channel = CHANNEL_ID
            else:
                channel = f"@{CHANNEL_ID}"
            
            # Try to get participant info
            entity = await self.client.get_entity(channel)
            participant = await self.client.get_permissions(entity, user_id)
            
            # If we get here without exception, user is subscribed
            return True
        except UserNotParticipantError:
            # User is not subscribed
            return False
        except (ChatAdminRequiredError, ValueError, PeerIdInvalidError):
            # Bot doesn't have admin rights or invalid channel
            # Alternative method: try to invite user (to check if they're not banned/subscribed)
            try:
                entity = await self.client.get_entity(channel)
                # Try to get full channel info which might reveal subscription status
                full_channel = await self.client.get_entity(entity)
                # This is a fallback - in practice, you might want to log this issue
                # since proper subscription checking requires bot admin rights
                return False
            except Exception:
                return False
        except Exception as e:
            print(f"Subscription check error: {e}")
            return False
    
    def generate_movie_id(self):
        """Generate unique movie ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_language_text(self, language, key):
        """Get translated text based on language"""
        texts = {
            'en': {
                'start': '🎬 Welcome to Movie Bot! Please select your language.',
                'select_language': 'Select Language:',
                'uzbek': 'Uzbek',
                'russian': 'Russian',
                'english': 'English',
                'main_menu': 'Main Menu',
                'movies': 'Movies',
                'watch_later': 'Watch Later',
                'watched': 'Watched',
                'search': 'Search Movies',
                'my_account': 'My Account',
                'admin_panel': 'Admin Panel',
                'enter_movie_id': 'Enter movie ID:',
                'movie_not_found': 'Movie not found!',
                'movie_added': 'Movie added successfully!',
                'already_watched': 'You have already watched this movie.',
                'added_to_watch_later': 'Added to Watch Later!',
                'removed_from_watch_later': 'Removed from Watch Later!',
                'watch_later_empty': 'Your Watch Later list is empty.',
                'watched_empty': 'You haven\'t watched any movies yet.',
                'search_placeholder': 'Enter movie title or description...',
                'movie_details': 'Title: {}\nGenre: {}\nYear: {}\nViews: {}',
                'subscribe_channel': 'Please subscribe to our channel to use this bot!',
                'check_subscription': '✅ Check Subscription',
                'not_subscribed': 'You are not subscribed to the channel!',
                'subscribed': 'Thank you for subscribing! You can now use the bot.',
                'user_stats': '📊 Your Stats:\nMovies Watched: {}\nMovies in Watch Later: {}',
                'admin_welcome': 'Admin Panel',
                'add_movie': 'Add Movie',
                'manage_users': 'Manage Users',
                'movie_added_success': 'Movie added successfully!',
                'enter_movie_title': 'Enter movie title:',
                'enter_movie_description': 'Enter movie description:',
                'enter_movie_genre': 'Enter movie genre:',
                'enter_movie_year': 'Enter movie year:',
                'send_movie_file': 'Send movie file (video/document):',
                'movie_title': 'Title:',
                'movie_description': 'Description:',
                'movie_genre': 'Genre:',
                'movie_year': 'Year:',
                'movie_id': 'ID:',
                'all_users': 'All Users',
                'user_info': 'User: {}\nID: {}\nLanguage: {}\nSubscribed: {}',
                'delete_movie': 'Delete Movie',
                'enter_movie_id_to_delete': 'Enter movie ID to delete:',
                'movie_deleted': 'Movie deleted successfully!',
                'total_users': 'Total Users: {}',
                'total_movies': 'Total Movies: {}',
                'back': 'Back',
                'cancel': 'Cancel'
            },
            'ru': {
                'start': '🎬 Добро пожаловать в Movie Bot! Пожалуйста, выберите язык.',
                'select_language': 'Выберите язык:',
                'uzbek': 'Узбекский',
                'russian': 'Русский',
                'english': 'Английский',
                'main_menu': 'Главное меню',
                'movies': 'Фильмы',
                'watch_later': 'Смотреть позже',
                'watched': 'Просмотрено',
                'search': 'Поиск фильмов',
                'my_account': 'Мой аккаунт',
                'admin_panel': 'Панель администратора',
                'enter_movie_id': 'Введите ID фильма:',
                'movie_not_found': 'Фильм не найден!',
                'movie_added': 'Фильм успешно добавлен!',
                'already_watched': 'Вы уже смотрели этот фильм.',
                'added_to_watch_later': 'Добавлено в "Смотреть позже"!',
                'removed_from_watch_later': 'Удалено из "Смотреть позже"!',
                'watch_later_empty': 'Ваш список "Смотреть позже" пуст.',
                'watched_empty': 'Вы еще не посмотрели ни одного фильма.',
                'search_placeholder': 'Введите название фильма или описание...',
                'movie_details': 'Название: {}\nЖанр: {}\nГод: {}\nПросмотры: {}',
                'subscribe_channel': 'Пожалуйста, подпишитесь на наш канал, чтобы использовать этого бота!',
                'check_subscription': '✅ Проверить подписку',
                'not_subscribed': 'Вы не подписаны на канал!',
                'subscribed': 'Спасибо за подписку! Теперь вы можете использовать бота.',
                'user_stats': '📊 Ваши статистики:\nПросмотрено фильмов: {}\nФильмов в списке "Смотреть позже": {}',
                'admin_welcome': 'Панель администратора',
                'add_movie': 'Добавить фильм',
                'manage_users': 'Управление пользователями',
                'movie_added_success': 'Фильм успешно добавлен!',
                'enter_movie_title': 'Введите название фильма:',
                'enter_movie_description': 'Введите описание фильма:',
                'enter_movie_genre': 'Введите жанр фильма:',
                'enter_movie_year': 'Введите год фильма:',
                'send_movie_file': 'Отправьте файл фильма (видео/документ):',
                'movie_title': 'Название:',
                'movie_description': 'Описание:',
                'movie_genre': 'Жанр:',
                'movie_year': 'Год:',
                'movie_id': 'ID:',
                'all_users': 'Все пользователи',
                'user_info': 'Пользователь: {}\nID: {}\nЯзык: {}\nПодписка: {}',
                'delete_movie': 'Удалить фильм',
                'enter_movie_id_to_delete': 'Введите ID фильма для удаления:',
                'movie_deleted': 'Фильм успешно удален!',
                'total_users': 'Всего пользователей: {}',
                'total_movies': 'Всего фильмов: {}',
                'back': 'Назад',
                'cancel': 'Отмена'
            },
            'uz': {
                'start': '🎬 Movie Bot ga xush kelibsiz! Iltimos, tilni tanlang.',
                'select_language': 'Tilni tanlang:',
                'uzbek': 'O\'zbek',
                'russian': 'Ruscha',
                'english': 'Inglizcha',
                'main_menu': 'Bosh menyu',
                'movies': 'Filmlar',
                'watch_later': 'Keyinroq tomosha qilish',
                'watched': 'Tomashta',
                'search': 'Filmlarni qidirish',
                'my_account': 'Mening akkauntim',
                'admin_panel': 'Admin panel',
                'enter_movie_id': 'Film ID sini kiriting:',
                'movie_not_found': 'Film topilmadi!',
                'movie_added': 'Film muvaffaqiyatli qo\'shildi!',
                'already_watched': 'Siz allaqachon bu filmni tomosha qilgansiz.',
                'added_to_watch_later': 'Keyinroq tomosha qilishga qo\'shildi!',
                'removed_from_watch_later': 'Keyinroq tomosha qilishdan olib tashlandi!',
                'watch_later_empty': 'Sizning "Keyinroq tomosha qilish" ro\'yxatingiz bo\'sh.',
                'watched_empty': 'Siz hali hech qanday film tomosha qilmadingiz.',
                'search_placeholder': 'Film nomini yoki tavsifini kiriting...',
                'movie_details': 'Nomi: {}\nJanri: {}\nYili: {}\nTomosha qilganlar: {}',
                'subscribe_channel': 'Botdan foydalanish uchun kanalimizga obuna bo\'ling!',
                'check_subscription': '✅ Obunani tekshirish',
                'not_subscribed': 'Siz kanalga obuna bo\'lmadingiz!',
                'subscribed': 'Obuna bo\'lganingiz uchun tashakkur! Endi botdan foydalanishingiz mumkin.',
                'user_stats': '📊 Sizning statistikangiz:\nTomashta filmalar: {}\nKeyinroq tomosha qilishda: {}',
                'admin_welcome': 'Admin panel',
                'add_movie': 'Film qo\'shish',
                'manage_users': 'Foydalanuvchilarni boshqarish',
                'movie_added_success': 'Film muvaffaqiyatli qo\'shildi!',
                'enter_movie_title': 'Film nomini kiriting:',
                'enter_movie_description': 'Film tavsifini kiriting:',
                'enter_movie_genre': 'Film janrini kiriting:',
                'enter_movie_year': 'Film yilini kiriting:',
                'send_movie_file': 'Film faylini yuboring (video/hujjat):',
                'movie_title': 'Nomi:',
                'movie_description': 'Tavsifi:',
                'movie_genre': 'Janri:',
                'movie_year': 'Yili:',
                'movie_id': 'ID:',
                'all_users': 'Barcha foydalanuvchilar',
                'user_info': 'Foydalanuvchi: {}\nID: {}\nTil: {}\nObuna: {}',
                'delete_movie': 'Filmni o\'chirish',
                'enter_movie_id_to_delete': 'O\'chirish uchun film ID sini kiriting:',
                'movie_deleted': 'Film muvaffaqiyatli o\'chirildi!',
                'total_users': 'Jami foydalanuvchilar: {}',
                'total_movies': 'Jami filmalar: {}',
                'back': 'Ortga',
                'cancel': 'Bekor qilish'
            }
        }
        return texts.get(language, texts['en']).get(key, key)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.db.add_user(user.id, username=user.username, first_name=user.first_name, last_name=user.last_name)
        
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek", callback_data='lang_uz')],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            self.get_language_text('en', 'start'),
            reply_markup=reply_markup
        )
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        language = query.data.split('_')[1]
        self.db.update_language(query.from_user.id, language)
        
        # Check subscription
        is_subscribed = await self.check_subscription(query.from_user.id)
        self.db.update_subscription_status(query.from_user.id, 1 if is_subscribed else 0)
        
        if not is_subscribed:
            await self.send_subscription_message(query.from_user.id, context, language)
            return
        
        await self.show_main_menu(query.from_user.id, context, language)
    
    async def send_subscription_message(self, user_id, context, language):
        keyboard = [[InlineKeyboardButton(
            self.get_language_text(language, 'check_subscription'),
            url=f"https://t.me/{CHANNEL_ID.lstrip('@')}" if CHANNEL_ID.startswith('@') else f"https://t.me/{CHANNEL_ID}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=self.get_language_text(language, 'subscribe_channel'),
            reply_markup=reply_markup
        )
    
    async def show_main_menu(self, user_id, context, language):
        keyboard = [
            [KeyboardButton(self.get_language_text(language, 'movies'))],
            [KeyboardButton(self.get_language_text(language, 'search'))],
            [KeyboardButton(self.get_language_text(language, 'watch_later')), 
             KeyboardButton(self.get_language_text(language, 'watched'))],
            [KeyboardButton(self.get_language_text(language, 'my_account'))]
        ]
        
        if user_id in ADMIN_IDS:
            keyboard.append([KeyboardButton(self.get_language_text(language, 'admin_panel'))])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await context.bot.send_message(
            chat_id=user_id,
            text="🎬 " + self.get_language_text(language, 'main_menu'),
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text
        language = self.db.get_user(user.id)[4] if self.db.get_user(user.id) else 'en'
        
        # Check subscription first
        is_subscribed = await self.check_subscription(user.id)
        self.db.update_subscription_status(user.id, 1 if is_subscribed else 0)
        
        if not is_subscribed:
            await self.send_subscription_message(user.id, context, language)
            return
        
        if text == self.get_language_text(language, 'main_menu'):
            await self.show_main_menu(user.id, context, language)
        
        elif text == self.get_language_text(language, 'movies'):
            await self.show_movies(update, context, language)
        
        elif text == self.get_language_text(language, 'watch_later'):
            await self.show_watch_later(update, context, language)
        
        elif text == self.get_language_text(language, 'watched'):
            await self.show_watched(update, context, language)
        
        elif text == self.get_language_text(language, 'search'):
            await update.message.reply_text(
                self.get_language_text(language, 'search_placeholder')
            )
            context.user_data['waiting_for_search'] = True
        
        elif text == self.get_language_text(language, 'my_account'):
            await self.show_user_account(update, context, language)
        
        elif text == self.get_language_text(language, 'admin_panel') and user.id in ADMIN_IDS:
            await self.show_admin_panel(update, context, language)
        
        # Handle search input
        elif context.user_data.get('waiting_for_search'):
            context.user_data['waiting_for_search'] = False
            await self.search_movies(update, context, text, language)
        
        # Handle movie ID input
        elif context.user_data.get('waiting_for_movie_id'):
            context.user_data['waiting_for_movie_id'] = False
            await self.show_movie_by_id(update, context, text, language)
    
    async def show_movies(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        movies = self.db.get_all_movies()
        
        if not movies:
            await update.message.reply_text(self.get_language_text(language, 'movie_not_found'))
            return
        
        for movie in movies[:10]:  # Show first 10 movies
            keyboard = [
                [InlineKeyboardButton("🎬 Watch", callback_data=f'watch_{movie[1]}')],
                [InlineKeyboardButton("➕ Watch Later", callback_data=f'watch_later_{movie[1]}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            caption = self.get_language_text(language, 'movie_details').format(
                movie[2], movie[4], movie[5], movie[8]
            )
            
            if movie[7] == 'video':
                await update.message.reply_video(
                    video=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_document(
                    document=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
    
    async def show_movie_by_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE, movie_id, language):
        movie = self.db.get_movie_by_id(movie_id)
        
        if not movie:
            await update.message.reply_text(self.get_language_text(language, 'movie_not_found'))
            return
        
        keyboard = [
            [InlineKeyboardButton("🎬 Watch", callback_data=f'watch_{movie[1]}')],
            [InlineKeyboardButton("➕ Watch Later", callback_data=f'watch_later_{movie[1]}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = self.get_language_text(language, 'movie_details').format(
            movie[2], movie[4], movie[5], movie[8]
        )
        
        if movie[7] == 'video':
            await update.message.reply_video(
                video=movie[6],
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_document(
                document=movie[6],
                caption=caption,
                reply_markup=reply_markup
            )
    
    async def show_watch_later(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        user = update.effective_user
        movies = self.db.get_watch_later(user.id)
        
        if not movies:
            await update.message.reply_text(self.get_language_text(language, 'watch_later_empty'))
            return
        
        for movie in movies:
            keyboard = [
                [InlineKeyboardButton("🎬 Watch", callback_data=f'watch_{movie[1]}')],
                [InlineKeyboardButton("❌ Remove", callback_data=f'remove_watch_later_{movie[1]}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            caption = self.get_language_text(language, 'movie_details').format(
                movie[2], movie[4], movie[5], movie[8]
            )
            
            if movie[7] == 'video':
                await update.message.reply_video(
                    video=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_document(
                    document=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
    
    async def show_watched(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        user = update.effective_user
        movies = self.db.get_watched_movies(user.id)
        
        if not movies:
            await update.message.reply_text(self.get_language_text(language, 'watched_empty'))
            return
        
        for movie in movies:
            keyboard = [[InlineKeyboardButton("🎬 Watch Again", callback_data=f'watch_{movie[1]}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            caption = self.get_language_text(language, 'movie_details').format(
                movie[2], movie[4], movie[5], movie[8]
            )
            
            if movie[7] == 'video':
                await update.message.reply_video(
                    video=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_document(
                    document=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
    
    async def search_movies(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query, language):
        movies = self.db.search_movies(query)
        
        if not movies:
            await update.message.reply_text(self.get_language_text(language, 'movie_not_found'))
            return
        
        for movie in movies[:10]:  # Show first 10 results
            keyboard = [
                [InlineKeyboardButton("🎬 Watch", callback_data=f'watch_{movie[1]}')],
                [InlineKeyboardButton("➕ Watch Later", callback_data=f'watch_later_{movie[1]}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            caption = self.get_language_text(language, 'movie_details').format(
                movie[2], movie[4], movie[5], movie[8]
            )
            
            if movie[7] == 'video':
                await update.message.reply_video(
                    video=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_document(
                    document=movie[6],
                    caption=caption,
                    reply_markup=reply_markup
                )
    
    async def show_user_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        user = update.effective_user
        stats = self.db.get_user_stats(user.id)
        
        message = self.get_language_text(language, 'user_stats').format(
            stats['watched_count'],
            stats['watch_later_count']
        )
        
        await update.message.reply_text(message)
    
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        keyboard = [
            [KeyboardButton(self.get_language_text(language, 'add_movie'))],
            [KeyboardButton(self.get_language_text(language, 'manage_users'))],
            [KeyboardButton(self.get_language_text(language, 'delete_movie'))],
            [KeyboardButton(self.get_language_text(language, 'back'))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        stats = {
            'users': len(self.db.get_all_users()),
            'movies': self.db.get_movies_count()
        }
        
        message = f"{self.get_language_text(language, 'admin_welcome')}\n\n"
        message += f"{self.get_language_text(language, 'total_users').format(stats['users'])}\n"
        message += f"{self.get_language_text(language, 'total_movies').format(stats['movies'])}"
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        language = self.db.get_user(user.id)[4] if self.db.get_user(user.id) else 'en'
        
        # Check subscription
        is_subscribed = await self.check_subscription(user.id)
        self.db.update_subscription_status(user.id, 1 if is_subscribed else 0)
        
        if not is_subscribed:
            await self.send_subscription_message(user.id, context, language)
            return
        
        data = query.data
        
        if data.startswith('watch_'):
            movie_id = data.split('_')[1]
            movie = self.db.get_movie_by_id(movie_id)
            
            if movie:
                # Add to watched
                user_info = self.db.get_user(user.id)
                if user_info:
                    self.db.add_to_watched(user_info[0], movie_id)
                
                # Send the movie
                if movie[7] == 'video':
                    await query.message.reply_video(video=movie[6])
                else:
                    await query.message.reply_document(document=movie[6])
        
        elif data.startswith('watch_later_'):
            movie_id = data.split('_')[2]
            user_info = self.db.get_user(user.id)
            if user_info:
                self.db.add_to_watch_later(user_info[0], movie_id)
                await query.edit_message_text(self.get_language_text(language, 'added_to_watch_later'))
        
        elif data.startswith('remove_watch_later_'):
            movie_id = data.split('_')[2]
            user_info = self.db.get_user(user.id)
            if user_info:
                self.db.remove_from_watch_later(user_info[0], movie_id)
                await query.edit_message_text(self.get_language_text(language, 'removed_from_watch_later'))
    
    async def handle_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        language = self.db.get_user(user.id)[4] if self.db.get_user(user.id) else 'en'
        
        if user.id not in ADMIN_IDS:
            return
        
        # This is a simplified version - in a real implementation, you'd need to handle
        # the multi-step process of adding a movie (title, description, etc.)
        file = update.message.video or update.message.document
        if file:
            file_id = file.file_id
            file_type = 'video' if update.message.video else 'document'
            
            # Generate movie ID
            movie_id = self.generate_movie_id()
            
            # You would need to store this in context.user_data and continue the process
            await update.message.reply_text(
                f"Movie file received. ID: {movie_id}. Please continue with /addmovie command."
            )

def main():
    bot_instance = MovieBot()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", bot_instance.start_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_message))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, bot_instance.handle_file_upload))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(bot_instance.handle_callback_query))
    
    # Language selection handler
    application.add_handler(CallbackQueryHandler(bot_instance.handle_language_selection, pattern='^lang_'))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
