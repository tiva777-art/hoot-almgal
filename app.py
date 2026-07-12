import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import requests
from bs4 import BeautifulSoup
import string
import random
import time
from datetime import datetime
from telegram import ReplyKeyboardRemove 
import nest_asyncio
import json
import csv
import os

# ==================== توكن البوت ====================
BOT_TOKEN = "7591229217:AAF8uVDVTILvevhVRIx0ny70LOtFo1LjL_U"

# ==================== إدارة الأدمن ====================

class AdminManager:
    def __init__(self):
        self.data_file = "admin_data.json"
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = data.get("users", {})
                self.banned_users = data.get("banned_users", [])
                self.stats = data.get("stats", {
                    "total_users": 0,
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "successful_invitations": 0,
                    "failed_invitations": 0
                })
                self.daily_reports = data.get("daily_reports", {})
        except:
            self.users = {}
            self.banned_users = []
            self.stats = {
                "total_users": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "successful_invitations": 0,
                "failed_invitations": 0
            }
            self.daily_reports = {}
            self.save_data()
    
    def save_data(self):
        data = {
            "users": self.users,
            "banned_users": self.banned_users,
            "stats": self.stats,
            "daily_reports": self.daily_reports
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id, username, first_name):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "username": username,
                "first_name": first_name,
                "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "operations": 0,
                "successful_ops": 0,
                "failed_ops": 0
            }
            self.stats["total_users"] = len(self.users)
            self.save_data()
    
    def update_stats(self, operation_type, success=True):
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.daily_reports:
            self.daily_reports[today] = {
                "successful_operations": 0,
                "failed_operations": 0,
                "successful_invitations": 0,
                "failed_invitations": 0
            }
        
        if operation_type == "operation":
            if success:
                self.stats["successful_operations"] += 1
                self.daily_reports[today]["successful_operations"] += 1
            else:
                self.stats["failed_operations"] += 1
                self.daily_reports[today]["failed_operations"] += 1
        
        elif operation_type == "invitation":
            if success:
                self.stats["successful_invitations"] += 1
                self.daily_reports[today]["successful_invitations"] += 1
            else:
                self.stats["failed_invitations"] += 1
                self.daily_reports[today]["failed_invitations"] += 1
        
        self.save_data()
    
    def ban_user(self, user_id):
        if user_id not in self.banned_users:
            self.banned_users.append(user_id)
            self.save_data()
            return True
        return False
    
    def unban_user(self, user_id):
        if user_id in self.banned_users:
            self.banned_users.remove(user_id)
            self.save_data()
            return True
        return False
    
    def is_banned(self, user_id):
        return user_id in self.banned_users
    
    def get_daily_report(self, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.daily_reports.get(date, {
            "successful_operations": 0,
            "failed_operations": 0,
            "successful_invitations": 0,
            "failed_invitations": 0
        })

# ==================== إنشاء مدير الأدمن ====================

admin_manager = AdminManager()
ADMINS = [1444139300]  # ضع رقمك هنا

def is_admin(user_id):
    return user_id in ADMINS

# ==================== دوال الكود الأصلي ====================

def generation_link(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def get_authorization(number, password, attempt_num):
    try:
        with requests.Session() as req:
            url_action = f'https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/auth?client_id=website&redirect_uri=https%3A%2F%2Fweb.vodafone.com.eg%2Far%2FKClogin&state=286d1217-db14-4846-86c1-9539beea01ed&response_mode=query&response_type=code&scope=openid&nonce={generation_link(10)}&kc_locale=en'
            
            response_url_action = req.get(url_action)
            soup = BeautifulSoup(response_url_action.content, 'html.parser')
            get_url_action = soup.find('form').get('action')
            
            header_request = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en;q=0.9,ar;q=0.8,ar-EG;q=0.7,en-US;q=0.6',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'web.vodafone.com.eg',
                'Origin': 'https://web.vodafone.com.eg',
                'Referer': url_action,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            
            data = {
                'username': number,
                'password': password
            }
            
            response_login = req.post(get_url_action, headers=header_request, data=data)
            check_login = response_login.url
            _check_KClogin = check_login.find('KClogin')
            
            if _check_KClogin != -1:
                _code = check_login[check_login.index('code=') + 5:]
                
                header_access_token = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-GB,en;q=0.9,ar;q=0.8,ar-EG;q=0.7,en-US;q=0.6',
                    'Connection': 'keep-alive',
                    'Content-type': 'application/x-www-form-urlencoded',
                    'Host': 'web.vodafone.com.eg',
                    'Origin': 'https://web.vodafone.com.eg',
                    'Referer': 'https://web.vodafone.com.eg/ar/KClogin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
                }
                
                data_access_token = {
                    'code': _code,
                    'grant_type': 'authorization_code',
                    'client_id': 'website',
                    'redirect_uri': 'https://web.vodafone.com.eg/ar/KClogin'
                }
                
                send_data_access_token = req.post(
                    'https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token',
                    headers=header_access_token, 
                    data=data_access_token
                )
                
                jwt = send_data_access_token.json()['access_token']
                return {"status": "success", "token": "Bearer " + jwt}
            else:
                return {"status": "error", "message": "الرقم أو كلمة السر غير صحيحة"}
    except Exception as e:
        return {"status": "error", "message": f"خطأ في تسجيل الدخول: {e}"}

def send_invitation(owner_number, member_number, token, percentage=40, attempt_num=1):
    try:
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'EN',
            'Authorization': token,
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://web.vodafone.com.eg',
            'Referer': 'https://web.vodafone.com.eg/spa/familySharing/manageFamily',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            "User-Agent": "okhttp/4.11.0",
            "x-agent-operatingsystem": "11",
            "clientId": "AnaVodafoneAndroid",
            "x-agent-device": "Samsung_Galaxy_A52",
            "x-agent-version": "2024.7.1",
            "x-agent-build": "600",
            'msisdn': owner_number,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
        }

        json_data = {
            'name': 'FlexFamily',
            'type': 'SendInvitation',
            'category': [
                {'value': '523', 'listHierarchyId': 'PackageID'},
                {'value': '47', 'listHierarchyId': 'TemplateID'},
                {'value': '523', 'listHierarchyId': 'TierID'},
                {'value': 'percentage', 'listHierarchyId': 'familybehavior'},
            ],
            'parts': {
                'member': [
                    {'id': [{'value': owner_number, 'schemeName': 'MSISDN'}], 'type': 'Owner'},
                    {'id': [{'value': member_number, 'schemeName': 'MSISDN'}], 'type': 'Member'},
                ],
                'characteristicsValue': {
                    'characteristicsValue': [
                        {'characteristicName': 'quotaDist1', 'value': percentage, 'type': 'percentage'},
                    ],
                },
            },
        }

        response = requests.patch(
            'https://mobile.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup',
            headers=headers,
            json=json_data,
        )
        
        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 201],
            "response_text": response.text,
            "attempt_num": attempt_num
        }
            
    except Exception as e:
        return {
            "status_code": 0,
            "success": False,
            "response_text": f"خطأ: {e}",
            "attempt_num": attempt_num
        }

def accept_invitation(owner_number, member_number, token):
    try:
        url = "https://mobile.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
        headers = {
            "api-host": "ProductOrderingManagement",
            "useCase": "MIProfile",
            "Authorization": token,
            "api-version": "v2",
            "x-agent-operatingsystem": "11",
            "clientId": "AnaVodafoneAndroid",
            "x-agent-device": "Samsung_Galaxy_A52",
            "x-agent-version": "2024.7.1",
            "x-agent-build": "600",
            "msisdn": member_number,
            "Accept": "application/json",
            "Accept-Language": "ar",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "mobile.vodafone.com.eg",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.11.0"
        }
        
        data = {
            "category": [{"listHierarchyId": "TemplateID", "value": "47"}],
            "name": "FlexFamily",
            "parts": {
                "member": [
                    {"id": [{"schemeName": "MSISDN", "value": owner_number}], "type": "Owner"},
                    {"id": [{"schemeName": "MSISDN", "value": member_number}], "type": "Member"}
                ]
            },
            "type": "AcceptInvitation"
        }
        
        response = requests.patch(url, headers=headers, json=data)
        response_text = response.text
        
        if response.status_code in [200, 201] or response_text == '{}':
            return {"success": True, "message": "تم قبول الدعوة بنجاح"}
        elif "Customer not eligible-Family member" in response_text:
            return {"success": True, "message": "العضو موجود بالفعل في عائلة"}
        else:
            return {"success": False, "message": f"فشل قبول الدعوة: {response.status_code} - {response_text}"}
            
    except Exception as e:
        return {"success": False, "message": f"خطأ في قبول الدعوة: {e}"}

def remove_member_with_token(ownerNum, token, memberNum):
    try:
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': token,
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-A526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
            'Origin': 'https://web.vodafone.com.eg',
            'Referer': 'https://web.vodafone.com.eg/spa/familySharing/manageFamily',
            'x-agent-operatingsystem': '11',
            'clientId': 'AnaVodafoneAndroid',
            'x-agent-device': 'Samsung_Galaxy_A52',
            'x-agent-version': '2024.7.1',
            'x-agent-build': '600',
            'msisdn': ownerNum,
        }

        payload = {
            "name": "FlexFamily",
            "type": "FamilyRemoveMember",
            "category": [{"value": "47", "listHierarchyId": "TemplateID"}],
            "parts": {
                "member": [
                    {"id": [{"value": ownerNum, "schemeName": 'MSISDN'}], "type": "Owner"},
                    {"id": [{"value": memberNum, "schemeName": 'MSISDN'}], "type": "Member"}
                ],
                "characteristicsValue": {
                    "characteristicsValue": [
                        {"characteristicName": "Disconnect", "value": "0"},
                        {"characteristicName": "LastMemberDeletion", "value": "1"}
                    ]
                }
            }
        }
        
        response = requests.patch(
            'https://mobile.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup',
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return {"success": True, "message": "تم الحذف بنجاح"}
        else:
            return {"success": False, "message": f"فشل في الحذف: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "message": f"حدث خطأ: {str(e)}"}

# ==================== دوال البوت ====================

GET_OWNER_NUMBER, GET_OWNER_PASSWORD, GET_MEMBER_NUMBER, GET_MEMBER_PASSWORD, GET_PERCENTAGE, GET_ATTEMPTS, GET_ACCEPT_TIME, CONFIRM_START = range(8)

user_sessions = {}

class BotSession:
    def __init__(self):
        self.owner_number = None
        self.owner_password = None
        self.member_number = None
        self.member_password = None
        self.percentage = 40
        self.attempts_count = 3
        self.accept_time = 30
        self.is_running = False
        self.current_update = None
        self.current_context = None
        self.owner_token = None
        self.member_token = None
        self.process_completed = False

    async def send_status(self, message, parse_markdown=True):
        if self.current_update and self.current_context:
            try:
                if parse_markdown:
                    await self.current_context.bot.send_message(
                        chat_id=self.current_update.effective_chat.id,
                        text=message,
                        parse_mode='Markdown'
                    )
                else:
                    await self.current_context.bot.send_message(
                        chat_id=self.current_update.effective_chat.id,
                        text=message
                    )
            except Exception as e:
                try:
                    await self.current_context.bot.send_message(
                        chat_id=self.current_update.effective_chat.id,
                        text=message
                    )
                except Exception as e2:
                    print(f"Error sending message: {e2}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # تتبع المستخدم في نظام الأدمن
    admin_manager.add_user(
        user_id, 
        update.effective_user.username, 
        update.effective_user.first_name
    )
    
    # التحقق إذا كان محظور
    if admin_manager.is_banned(user_id):
        await update.message.reply_text("❌ أنت محظور من استخدام البوت.")
        return
    
    if user_id in user_sessions:
        old_session = user_sessions[user_id]
        old_session.is_running = False
        await asyncio.sleep(1)
    
    user_sessions[user_id] = BotSession()
    session = user_sessions[user_id]
    
    user_name = update.effective_user.first_name or "عزيزي"
    welcome_text = f"""
🎯 مرحباً بك يا {user_name} في بوت تطير افراد الخاص بـ *wolves shop egypt* 

🔸 *سيطلب منك:*
1. 📱 رقم الأونر
2. 🔑 كلمة سر الأونر  
3. 👥 رقم العضو المراد إرسال الدعوة له
4. 📊 النسبة الفليكس

🚀 *لنبدأ الآن!*

أرسل لي رقم الأونر:
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def get_owner_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    
    owner_number = update.message.text.strip()
    
    is_valid, message = validate_phone_number(owner_number)
    if not is_valid:
        keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
        await update.message.reply_text(
            message + "\n\n📱 الرجاء إرسال رقم الأونر الصحيح (11 رقم يبدأ بـ 01):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        session.owner_number = owner_number
        keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
        await update.message.reply_text(
            "🔑 الرجاء إرسال كلمة سر الأونر:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def stop_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        session = user_sessions.get(user_id)
        
        if not session:
            await update.message.reply_text("ℹ️ لا توجد عمليات جارية حالياً")
            return
        
        if session.is_running:
            session.is_running = False
            remove_keyboard = ReplyKeyboardRemove()
            await update.message.reply_text("⏹️ تم إيقاف العملية بنجاح", reply_markup=remove_keyboard)
            return
        else:
            await update.message.reply_text("ℹ️ لا توجد عمليات جارية حالياً")
            
    except Exception as e:
        print(f"Error in stop handler: {e}")

async def get_owner_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    
    session.owner_password = update.message.text
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
    
    await update.message.reply_text(
        "📱 الرجاء إرسال رقم العضو:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_MEMBER_NUMBER

async def get_member_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effe#ctive_user.id
    session = user_sessions[user_id]
    
    member_number = update.message.text.strip()
    
    is_valid, message = validate_phone_number(member_number)
    if not is_valid:
        keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
        await update.message.reply_text(
            message + "\n\n📱 الرجاء إرسال رقم العضو الصحيح (11 رقم يبدأ بـ 01):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return GET_MEMBER_NUMBER
    
    if member_number == session.owner_number:
        keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
        await update.message.reply_text(
            "❌ رقم العضو لا يمكن أن يكون نفس رقم الأونر\n\n📱 الرجاء إرسال رقم عضو مختلف:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return GET_MEMBER_NUMBER
    
    session.member_number = member_number
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]]
    
    await update.message.reply_text(
        "🔑 الرجاء إرسال كلمة سر العضو:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_MEMBER_PASSWORD

async def get_member_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    
    session.member_password = update.message.text
    
    if session.member_number == session.owner_number:
        await update.message.reply_text("❌ خطأ: رقم العضو لا يمكن أن يكون نفس رقم الأونر\n\n🔁 الرجاء البدء من جديد باستخدام /start")
        return ConversationHandler.END
    
    await update.message.reply_text("🔐 جاري تسجيل دخول الأونر...")
    owner_login_result = get_authorization(session.owner_number, session.owner_password, "أونر")
    
    if owner_login_result["status"] != "success":
        admin_manager.update_stats("operation", False)
        await update.message.reply_text(f"❌ فشل تسجيل دخول الأونر: {owner_login_result['message']}")
        return ConversationHandler.END
    
    await update.message.reply_text("🔐 جاري تسجيل دخول العضو...")
    member_login_result = get_authorization(session.member_number, session.member_password, "عضو")
    
    if member_login_result["status"] != "success":
        admin_manager.update_stats("operation", False)
        await update.message.reply_text(f"❌ فشل تسجيل دخول العضو: {member_login_result['message']}")
        return ConversationHandler.END
    
    await update.message.reply_text("✅ تم التحقق من بيانات الحسابين بنجاح")
    
    keyboard = [
        [InlineKeyboardButton("10%", callback_data="percentage_10")],
        [InlineKeyboardButton("20%", callback_data="percentage_20")],
        [InlineKeyboardButton("40%", callback_data="percentage_40")],
        [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]
    ]
    
    await update.message.reply_text(
        "📊 اختر نسبة المشاركة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_PERCENTAGE

async def get_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_sessions[user_id]
    
    if query.data == "cancel_process":
        await cancel(update, context)
        return ConversationHandler.END
    
    if query.data == "percentage_10":
        session.percentage = 10
    elif query.data == "percentage_20":
        session.percentage = 20
    elif query.data == "percentage_40":
        session.percentage = 40
    
    keyboard = [
        [InlineKeyboardButton("1", callback_data="attempts_1")],
        [InlineKeyboardButton("3", callback_data="attempts_3")],
        [InlineKeyboardButton("5", callback_data="attempts_5")],
        [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]
    ]
    
    await query.edit_message_text(
        "🔄 اختر عدد المحاولات:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_ATTEMPTS

async def get_attempts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_sessions[user_id]
    
    if query.data == "cancel_process":
        await cancel(update, context)
        return ConversationHandler.END
    
    if query.data == "attempts_1":
        session.attempts_count = 1
    elif query.data == "attempts_3":
        session.attempts_count = 3
    elif query.data == "attempts_5":
        session.attempts_count = 5
    
    keyboard = [
        [
            InlineKeyboardButton("30 ثانية", callback_data="time_30"),
            InlineKeyboardButton("1 دقيقة", callback_data="time_60")
        ],
        [
            InlineKeyboardButton("3 دقائق", callback_data="time_180"),
            InlineKeyboardButton("5 دقائق", callback_data="time_300")
        ],
        [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_process")]
    ]
    
    await query.edit_message_text(
        "⏱️ اختر وقت القبول:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_ACCEPT_TIME

async def get_accept_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_sessions[user_id]
    
    if query.data == "cancel_process":
        await cancel(update, context)
        return ConversationHandler.END
    
    if query.data == "time_30":
        session.accept_time = 30
    elif query.data == "time_60":
        session.accept_time = 60
    elif query.data == "time_180":
        session.accept_time = 180
    elif query.data == "time_300":
        session.accept_time = 300
    
    summary_text = f"""
✨ ملخص البيانات ✨

📱 رقم الفرد: {session.member_number}
👑 رقم المالك: {session.owner_number}
🔄 عدد المحاولات: {session.attempts_count}
📊 نسبة الحصة: {session.percentage}%
⏱️ وقت القبول: {session.accept_time} ثانية

هل تريد بدء العملية الآن؟
"""
    
    keyboard = [
        [InlineKeyboardButton("نعم ابدأ ✅", callback_data="start_process")],
        [InlineKeyboardButton("لا ❌", callback_data="cancel_process")]
    ]
    
    await query.edit_message_text(
        summary_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def handle_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await cancel(update, context)

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    
    if not session:
        await query.edit_message_text("❌ انتهت الجلسة، يرجى البدء من جديد")
        return ConversationHandler.END
    
    if query.data == "start_process":
        if session.is_running:
            await query.edit_message_text("⚠️ العملية شغالة بالفعل!")
            return ConversationHandler.END
            
        session.current_update = update
        session.current_context = context
        session.is_running = True
        
        stop_keyboard = [
            [KeyboardButton("⏹️ ايقاف العملية")]
        ]
        stop_reply_markup = ReplyKeyboardMarkup(stop_keyboard, resize_keyboard=True, one_time_keyboard=False)
        
        await query.edit_message_text("🚀 بدء العملية...")
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="⏹️ يمكنك إيقاف العملية في أي وقت باستخدام الزر أدناه:",
            reply_markup=stop_reply_markup
        )
        
        threading.Thread(target=run_async_in_thread, args=(session,)).start()
        
    else:
        await query.edit_message_text("❌ تم إلغاء العملية")
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    return ConversationHandler.END

def run_async_in_thread(session):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(execute_invitation_process(session))
    except Exception as e:
        print(f"❌ Error in thread: {e}")
    finally:
        session.is_running = False
        session.process_completed = True
        try:
            if not loop.is_closed():
                loop.stop()
                loop.close()
        except:
            pass
        asyncio.set_event_loop(None)

async def execute_invitation_process(session):
    try:
        for attempt in range(session.attempts_count):
            if not session.is_running:
                return
                
            attempt_num = attempt + 1
            
            if not session.is_running:
                return
            await session.send_status(f"🔄 المحاولة {attempt_num}/{session.attempts_count} - جاري الحصول على 4 توكنز...", False)
            
            max_token_attempts = 5
            token_wait_time = 5
            tokens = []
            
            for token_attempt in range(max_token_attempts):
                if not session.is_running:
                    return
                    
                current_attempt = token_attempt + 1
                needed_tokens = 4 - len(tokens)
                
                if needed_tokens <= 0:
                    break
                
                await session.send_status(f"🔐 محاولة التوكن {current_attempt}/{max_token_attempts} - ناقص {needed_tokens} توكنز", False)
                
                new_tokens = await get_multiple_tokens(session, needed_tokens)
                tokens.extend(new_tokens)
                
                if len(tokens) < 4 and current_attempt < max_token_attempts:
                    await session.send_status(f"⏰ حصلنا على {len(tokens)}/4 توكنز - ننتظر 5 ثواني للمحاولة التالية...", False)
                    await asyncio.sleep(token_wait_time)
            
            if not session.is_running:
                return
            
            if len(tokens) == 0:
                admin_manager.update_stats("operation", False)
                await session.send_status("❌ فشل في الحصول على أي توكنز", False)
                if attempt_num < session.attempts_count:
                    wait_time = 60
                    if not session.is_running:
                        return
                    await session.send_status("⏰ انتظار 1 دقائق لضمان المحاولة القادمة...", False)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    if not session.is_running:
                        return
                    await session.send_status("❌ فشل في الحصول على توكنز - جاري الحذف...", False)
                    await execute_delete_process(session, tokens)
                    break
                
            if not session.is_running:
                return
            await session.send_status(f"✅ تم الحصول على {len(tokens)} توكنز بنجاح", False)
            
            results = []
            
            def send_invitation_thread(token, invitation_attempt_num):
                if not session.is_running:
                    return
                result = send_invitation(
                    session.owner_number,
                    session.member_number,
                    token,
                    session.percentage,
                    invitation_attempt_num
                )
                results.append(result)
            
            invitation_threads = []
            for i, token in enumerate(tokens):
                if not session.is_running:
                    break
                thread = threading.Thread(
                    target=send_invitation_thread, 
                    args=(token, i+1)
                )
                invitation_threads.append(thread)
                thread.start()
            
            for thread in invitation_threads:
                thread.join()
            
            if not session.is_running:
                return
            
            results_text = "📊 نتائج الدعوات:\n\n"
            for i, result in enumerate(results):
                status_icon = "✅" if result["success"] else "❌"
                status_text = "تم الإرسال" if result["success"] else "فشل الإرسال"
                results_text += f"الدعوة {i+1}: {status_icon} {status_text} - كود: {result['status_code']}\n"
            
            if session.is_running:
                await session.send_status(results_text, False)
            
            successful_invitations = sum(1 for r in results if r["success"])
            
            if successful_invitations >= 2:
                admin_manager.update_stats("invitation", True)
                if not session.is_running:
                    return
                await session.send_status(f"🎯 تم نجاح {successful_invitations}/{len(tokens)} دعوة - جاري قبول الدعوة...", False)
                
                if not session.is_running:
                    return
                await session.send_status(f"⏰ انتظار {session.accept_time} ثانية قبل القبول...", False)
                await asyncio.sleep(session.accept_time)
                
                if not session.is_running:
                    return
                
                await session.send_status("🤝 جاري قبول الدعوة...", False)
                
                max_accept_attempts = 10
                accept_wait_time = 180
                
                for accept_attempt in range(max_accept_attempts):
                    if not session.is_running:
                        return
                    
                    accept_attempt_num = accept_attempt + 1
                    
                    await session.send_status(f"🔄 محاولة القبول {accept_attempt_num}/{max_accept_attempts}...", False)
                    
                    await session.send_status("🔐 جاري تسجيل دخول العضو للقبول...", False)
                    member_login_result = get_authorization(session.member_number, session.member_password, f"قبول {accept_attempt_num}")

                    if member_login_result["status"] == "success":
                        accept_result = accept_invitation(
                            session.owner_number,
                            session.member_number,
                            member_login_result["token"]
                        )
                        
                        if accept_result["success"]:
                            admin_manager.update_stats("operation", True)
                            await session.send_status(f"🎉 {accept_result['message']}", False)
                            await session.send_status("✅ تم إكمال العملية بنجاح!", False)
                            return
                        else:
                            await session.send_status(f"❌ فشل في القبول: {accept_result['message']}", False)
                    else:
                        await session.send_status(f"❌ فشل تسجيل دخول العضو: {member_login_result['message']}", False)
                    
                    if accept_attempt_num >= max_accept_attempts:
                        await session.send_status("❌ انتهت جميع محاولات القبول", False)
                        break
                    
                    await session.send_status(f"⏰ انتظار 3 دقائق قبل المحاولة التالية للقبول...", False)
                    await asyncio.sleep(accept_wait_time)
                
                if attempt_num < session.attempts_count:
                    wait_time = 60
                    await session.send_status("⏰ انتظار 1 دقيقة للمحاولة التالية...", False)
                    await asyncio.sleep(wait_time)
            
            else:
                admin_manager.update_stats("invitation", False)
                await session.send_status(f"❌ نجحت {successful_invitations}/{len(tokens)} دعوة فقط - جاري الحذف المباشر...", False)
                
                await execute_delete_process(session, tokens)
                
                if attempt_num == session.attempts_count:
                    return
                else:
                    wait_time = 60
                    await session.send_status("⏰ انتظار 1 دقائق لضمان المحاولة القادمة...", False)
                    await asyncio.sleep(wait_time)
    
    except Exception as e:
        error_msg = f"❌ خطأ في العملية: {str(e)}"
        print(error_msg)
        if session.is_running:
            await session.send_status(error_msg, False)
    finally:
        session.is_running = False
        session.process_completed = True

async def get_multiple_tokens(session, count):
    tokens = []
    
    def login_attempt(attempt_num):
        if not session.is_running:
            return
        try:
            login_result = get_authorization(session.owner_number, session.owner_password, f"توكن {attempt_num}")
            if login_result["status"] == "success":
                tokens.append(login_result["token"])
        except Exception as e:
            print(f"خطأ في محاولة التوكن {attempt_num}: {e}")
    
    login_threads = []
    for i in range(count):
        if not session.is_running:
            break
        thread = threading.Thread(target=login_attempt, args=(i+1,))
        login_threads.append(thread)
        thread.start()
    
    for thread in login_threads:
        thread.join(timeout=30)
    
    return tokens

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        session = user_sessions[user_id]
        session.is_running = False
        del user_sessions[user_id]
    
    try:
        if update.callback_query:
            await update.callback_query.answer()
            chat_id = update.callback_query.message.chat_id
            
            try:
                await update.callback_query.message.edit_text("✅ تم إلغاء العملية")
            except Exception as edit_error:
                print(f"Edit error: {edit_error}")
                await context.bot.send_message(chat_id=chat_id, text="✅ تم إلغاء العملية")
            
        elif update.message:
            chat_id = update.message.chat_id
            await update.message.reply_text("✅ تم إلغاء العملية والعودة للرئيسية")
        else:
            chat_id = user_id
        
        user_sessions[user_id] = BotSession()
        session = user_sessions[user_id]
        
        user_name = update.effective_user.first_name or "عزيزي"
        welcome_text = f"""
🎯 مرحباً بك يا {user_name} في بوت تطير افراد الخاص بـ *wolves shop egypt* 

🔸 *سيطلب منك:*
1. 📱 رقم الأونر
2. 🔑 كلمة سر الأونر  
3. 👥 رقم العضو المراد إرسال الدعوة له
4. 📊 النسبة الفليكس

🚀 *لنبدأ الآن!*

أرسل لي رقم الأونر:
"""
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Error in cancel: {e}")
    
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text("ℹ️ لا توجد جلسة نشطة")
        return
    
    session = user_sessions[user_id]
    
    if session.is_running:
        status_text = "🟢 حالة العملية: جارية"
    else:
        status_text = "🔴 لا توجد عمليات جارية حالياً"
    
    await update.message.reply_text(status_text)

def validate_phone_number(number):
    if not number.isdigit():
        return False, "❌ الرقم يجب أن يحتوي على أرقام فقط"
    
    if len(number) != 11:
        return False, "❌ الرقم يجب أن يكون 11 رقماً"
    
    if not number.startswith('01'):
        return False, "❌ الرقم يجب أن يبدأ بـ 01"
    
    return True, "✅ الرقم صحيح"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 أوامر البوت:

/start - بدء عملية جديدة
/status - عرض حالة العملية
/cancel - إلغاء العملية الحالية
/help - عرض هذه المساعدة

🎯 مميزات البوت:
• إرسال دعوتين متزامنتين
• نظام محاولات متكررة
• قبول تلقائي بعد وقت محدد
• تحديثات فورية بالحالة
• إدارة كاملة للدعوات
"""
    await update.message.reply_text(help_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    print(f"حدث خطأ: {error}")
    
    if "event loop" in str(error) or "Event loop" in str(error):
        return
    
    if update and update.message:
        try:
            user_id = update.effective_user.id
            session = user_sessions.get(user_id)
            if session and session.is_running:
                await update.message.reply_text("⚠️ حدث خطأ مؤقت، جرب مرة أخرى")
        except:
            pass

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = BotSession()
        session = user_sessions[user_id]
        
        user_name = update.effective_user.first_name or "عزيزي"
        welcome_text = f"""
🎯 مرحباً بك يا {user_name} في بوت تطير افراد الخاص بـ *wolves shop egypt* 

🔸 *سيطلب منك:*
1. 📱 رقم الأونر
2. 🔑 كلمة سر الأونر  
3. 👥 رقم العضو المراد إرسال الدعوة له
4. 📊 النسبة الفليكس

🚀 *لنبدأ الآن!*

أرسل لي رقم الأونر:
"""
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        return
    
    session = user_sessions[user_id]
    text = update.message.text
    
    if text == "⏹️ ايقاف العملية":
        await stop_process_handler(update, context)
        return
    
    if session.owner_number is None:
        await get_owner_number(update, context)
    elif session.owner_password is None:
        await get_owner_password(update, context)
    elif session.member_number is None:
        await get_member_number(update, context)
    elif session.member_password is None:
        await get_member_password(update, context)
    else:
        await update.message.reply_text("ℹ️ البيانات مكتملة. استخدم /start لبدء عملية جديدة")
        
async def execute_delete_process(session, tokens):
    await session.send_status("🚨 بدء عملية الحذف المباشر...", False)
    
    delete_token = None
    if tokens:
        delete_token = tokens[0]
        await session.send_status("✅ استخدام توكن موجود للحذف", False)
    else:
        await session.send_status("🔐 جاري تسجيل دخول جديد للحذف...", False)
        login_result = get_authorization(session.owner_number, session.owner_password, "حذف")
        if login_result["status"] == "success":
            delete_token = login_result["token"]
            await session.send_status("✅ تم تسجيل الدخول للحذف", False)
        else:
            await session.send_status("❌ فشل تسجيل دخول للحذف", False)
            return
    
    retry_delays = [5, 120, 240]
    max_retries = 3
    
    for retry in range(max_retries):
        if not session.is_running:
            await session.send_status("⏹️ تم إيقاف العملية", False)
            return
            
        retry_num = retry + 1
        
        await session.send_status(
            f"🗑️ محاولة الحذف {retry_num}/{max_retries}", 
            False
        )
        
        delay = retry_delays[retry]
        await asyncio.sleep(delay)
        
        await session.send_status("🗑️ جاري محاولة الحذف التلقائي للعضو...", False)
        
        delete_result = remove_member_with_token(session.owner_number, delete_token, session.member_number)
        
        if delete_result["success"]:
            success_msg = f"""
🎉 تم الحذف بنجاح!

🛡️ تم حذف العضو بنجاح.
الرسالة: {delete_result['message']}
"""
            await session.send_status(success_msg, False)
            return
        else:
            error_msg = f"""
❌ فشل في الحذف - المحاولة {retry_num}

💬 الرسالة: {delete_result['message']}
"""
            await session.send_status(error_msg, False)
            
            if retry_num < max_retries:
                next_delay = retry_delays[retry_num] if retry_num < len(retry_delays) else 300
                await session.send_status(f"🔁 سيتم إعادة المحاولة بعد {next_delay} ثانية...", False)
    
    await session.send_status("❌ انتهت جميع محاولات الحذف", False)

# ==================== لوحة الأدمن ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لوحة تحكم الأدمن"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرفين فقط.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 إدارة الأعضاء", callback_data="admin_users")],
        [InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="admin_backup")],
        [InlineKeyboardButton("📅 تقرير اليوم", callback_data="admin_daily_report")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛠️ *لوحة تحكم الأدمن*\n\n"
        "اختر الإجراء المطلوب:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    query = update.callback_query
    await query.answer()
    
    stats = admin_manager.stats
    daily_report = admin_manager.get_daily_report()
    
    stats_text = f"""
📊 *إحصائيات البوت*

👥 عدد المستخدمين: `{stats['total_users']}`
✅ العمليات الناجحة: `{stats['successful_operations']}`
❌ العمليات الفاشلة: `{stats['failed_operations']}`
✅ دعوات ناجحة: `{stats['successful_invitations']}`
❌ دعوات فاشلة: `{stats['failed_invitations']}`

📈 *إحصائيات اليوم*
✅ عمليات ناجحة: `{daily_report['successful_operations']}`
❌ عمليات فاشلة: `{daily_report['failed_operations']}`
✅ دعوات ناجحة: `{daily_report['successful_invitations']}`
❌ دعوات فاشلة: `{daily_report['failed_invitations']}`
"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إدارة الأعضاء"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔨 حظر مستخدم", callback_data="admin_ban_user")],
        [InlineKeyboardButton("🔓 فك حظر مستخدم", callback_data="admin_unban_user")],
        [InlineKeyboardButton("📋 قائمة المحظورين", callback_data="admin_banned_list")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👥 *إدارة الأعضاء*\n\n"
        "اختر الإجراء المطلوب:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def ban_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال ID للحظر"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔨 *حظر مستخدم*\n\n"
        "أرسل ID المستخدم الذي تريد حظره:",
        parse_mode='Markdown'
    )
    context.user_data["awaiting_ban"] = True

async def unban_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال ID لفك الحظر"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔓 *فك حظر مستخدم*\n\n"
        "أرسل ID المستخدم الذي تريد فك حظره:",
        parse_mode='Markdown'
    )
    context.user_data["awaiting_unban"] = True

async def show_banned_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المحظورين"""
    query = update.callback_query
    await query.answer()
    
    banned_list = admin_manager.banned_users
    if not banned_list:
        text = "📋 *قائمة المحظورين*\n\nلا يوجد مستخدمين محظورين حالياً."
    else:
        text = "📋 *قائمة المحظورين*\n\n"
        for user_id in banned_list:
            text += f"🆔 `{user_id}`\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def broadcast_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال الرسالة الجماعية"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📢 *إرسال رسالة جماعية*\n\n"
        "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:\n"
        "يمكنك إرسال نص، صورة، فيديو، أو ملف PDF",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    context.user_data["awaiting_broadcast"] = True

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال الرسالة الجماعية"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id) or not context.user_data.get("awaiting_broadcast"):
        return
    
    message = update.message
    users = admin_manager.users
    successful = 0
    failed = 0
    
    progress_msg = await update.message.reply_text("🔄 جاري إرسال الرسالة الجماعية...")
    
    for user_id_str in users.keys():
        try:
            user_id_int = int(user_id_str)
            
            if admin_manager.is_banned(user_id_int):
                continue
            
            if message.text:
                await context.bot.send_message(
                    chat_id=user_id_int,
                    text=message.text
                )
            elif message.photo:
                await context.bot.send_photo(
                    chat_id=user_id_int,
                    photo=message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.video:
                await context.bot.send_video(
                    chat_id=user_id_int,
                    video=message.video.file_id,
                    caption=message.caption
                )
            elif message.document:
                await context.bot.send_document(
                    chat_id=user_id_int,
                    document=message.document.file_id,
                    caption=message.caption
                )
            
            successful += 1
            await asyncio.sleep(0.1)
            
        except Exception as e:
            failed += 1
            print(f"فشل إرسال لـ {user_id_str}: {e}")
    
    result_text = f"""
✅ *تم الانتهاء من الإرسال الجماعي*

✅ تم الإرسال بنجاح: `{successful}`
❌ فشل في الإرسال: `{failed}`
👥 الإجمالي: `{len(users)}`
"""
    
    await progress_msg.edit_text(result_text, parse_mode='Markdown')
    context.user_data["awaiting_broadcast"] = False

async def create_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء نسخة احتياطية"""
    query = update.callback_query
    await query.answer()
    
    csv_filename = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'username', 'first_name', 'join_date', 'operations', 'successful_ops', 'failed_ops']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for user_id, user_data in admin_manager.users.items():
            writer.writerow({
                'user_id': user_id,
                'username': user_data.get('username', ''),
                'first_name': user_data.get('first_name', ''),
                'join_date': user_data.get('join_date', ''),
                'operations': user_data.get('operations', 0),
                'successful_ops': user_data.get('successful_ops', 0),
                'failed_ops': user_data.get('failed_ops', 0)
            })
    
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=InputFile(csv_filename),
        caption=f"📦 النسخة الاحتياطية للمستخدمين\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    os.remove(csv_filename)
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✅ تم إنشاء النسخة الاحتياطية بنجاح وإرسالها.",
        reply_markup=reply_markup
    )

async def send_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال التقرير اليومي"""
    query = update.callback_query
    await query.answer()
    
    today = datetime.now().strftime("%Y-%m-%d")
    report = admin_manager.get_daily_report(today)
    
    report_text = f"""
📅 *تقرير اليوم - {today}*

✅ العمليات الناجحة: `{report['successful_operations']}`
❌ العمليات الفاشلة: `{report['failed_operations']}`
✅ دعوات ناجحة: `{report['successful_invitations']}`
❌ دعوات فاشلة: `{report['failed_invitations']}`

👥 إجمالي المستخدمين: `{admin_manager.stats['total_users']}`
"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(report_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كليبكات الأدمن"""
    query = update.callback_query
    data = query.data
    
    if data == "admin_stats":
        await show_stats(update, context)
    elif data == "admin_users":
        await manage_users(update, context)
    elif data == "admin_ban_user":
        await ban_user_prompt(update, context)
    elif data == "admin_unban_user":
        await unban_user_prompt(update, context)
    elif data == "admin_banned_list":
        await show_banned_list(update, context)
    elif data == "admin_broadcast":
        await broadcast_prompt(update, context)
    elif data == "admin_backup":
        await create_backup(update, context)
    elif data == "admin_daily_report":
        await send_daily_report(update, context)
    elif data == "admin_back":
        await admin_panel(update, context)

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النصوص في وضع الأدمن"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    text = update.message.text
    
    if context.user_data.get("awaiting_ban"):
        try:
            user_to_ban = int(text)
            if admin_manager.ban_user(user_to_ban):
                await update.message.reply_text(f"✅ تم حظر المستخدم `{user_to_ban}` بنجاح.", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"⚠️ المستخدم `{user_to_ban}` محظور بالفعل.", parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ الرجاء إدخال ID صحيح.")
        context.user_data["awaiting_ban"] = False
    
    elif context.user_data.get("awaiting_unban"):
        try:
            user_to_unban = int(text)
            if admin_manager.unban_user(user_to_unban):
                await update.message.reply_text(f"✅ تم فك حظر المستخدم `{user_to_unban}` بنجاح.", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"⚠️ المستخدم `{user_to_unban}` غير محظور.", parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ الرجاء إدخال ID صحيح.")
        context.user_data["awaiting_unban"] = False

async def auto_daily_report(context: ContextTypes.DEFAULT_TYPE):
    """إرسال التقرير اليومي تلقائياً"""
    today = datetime.now().strftime("%Y-%m-%d")
    report = admin_manager.get_daily_report(today)
    
    report_text = f"""
📊 *التقرير اليومي التلقائي - {today}*

✅ العمليات الناجحة: `{report['successful_operations']}`
❌ العمليات الفاشلة: `{report['failed_operations']}`
✅ دعوات ناجحة: `{report['successful_invitations']}`
❌ دعوات فاشلة: `{report['failed_invitations']}`

👥 إجمالي المستخدمين: `{admin_manager.stats['total_users']}`
"""
    
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(admin_id, report_text, parse_mode='Markdown')
        except Exception as e:
            print(f"فشل إرسال التقرير لـ {admin_id}: {e}")

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # handlers البوت الأصلي
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("cancel", cancel))
        application.add_handler(CommandHandler("admin", admin_panel))  # أمر الأدمن
        
        # handlers الكيبورد الإنلاين
        application.add_handler(CallbackQueryHandler(get_percentage, pattern='^percentage_'))
        application.add_handler(CallbackQueryHandler(get_attempts, pattern='^attempts_'))
        application.add_handler(CallbackQueryHandler(get_accept_time, pattern='^time_'))
        application.add_handler(CallbackQueryHandler(handle_cancel_callback, pattern='^cancel_process$'))
        application.add_handler(CallbackQueryHandler(handle_confirmation, pattern='^(start_process)$'))
        application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
        
        # handler لإيقاف العملية
        application.add_handler(MessageHandler(filters.Text("⏹️ ايقاف العملية"), stop_process_handler))
        
        # handler للرسائل النصية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_broadcast), group=1)
        
        application.add_error_handler(error_handler)
        
        # التقرير اليومي التلقائي
        #job_queue = application.job_queue
        #if job_queue:
            #job_queue.run_daily(auto_daily_report, time=datetime.time(hour=23, minute=59))
        
        print("🤖 البوت يعمل...")
        print("🛠️ لوحة الأدمن جاهزة - استخدم /admin")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        
if __name__ == "__main__":
    main()