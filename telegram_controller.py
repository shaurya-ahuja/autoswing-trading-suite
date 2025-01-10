"""
AutoSwing Trading Suite - Telegram Bot Controller
A Telegram interface for managing crypto trading bots.

Author: AutoSwing Team
License: MIT
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config
from exchange_client import CryptoExchange
from trading_bots import GridTradingEngine, DollarCostAverager

# Initialize Telegram bot and exchange connection
telegram_bot = telebot.TeleBot(config("TELEGRAM_BOT_TOKEN"))
crypto_exchange = CryptoExchange('binance')


def create_main_keyboard():
    """Create the main interactive menu keyboard."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Grid Trading", callback_data="guide_grid"),
        InlineKeyboardButton("💰 DCA Strategy", callback_data="guide_dca"),
    )
    keyboard.add(
        InlineKeyboardButton("💵 Check Balance", callback_data="show_balance"),
        InlineKeyboardButton("📈 Portfolio", callback_data="show_portfolio"),
    )
    keyboard.add(
        InlineKeyboardButton("❓ Help", callback_data="show_help")
    )
    return keyboard


@telegram_bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle the /start command - welcome message."""
    welcome_text = (
        "🚀 *Welcome to AutoSwing Trading Suite!*\n\n"
        "Your personal crypto trading assistant.\n"
        "Select an option below to get started:"
    )
    telegram_bot.reply_to(
        message, 
        welcome_text,
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )


@telegram_bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle all inline keyboard callbacks."""
    chat_id = call.message.chat.id
    
    if call.data == "guide_grid":
        guide_text = (
            "📊 *Grid Trading Setup*\n\n"
            "Place multiple buy orders at different price levels.\n\n"
            "*Command:* `/grid <pair> <levels> <min_price> <max_price>`\n"
            "*Example:* `/grid BTC/USDT 5 30000 35000`\n\n"
            "This creates 5 buy orders from $30k to $35k."
        )
        telegram_bot.send_message(chat_id, guide_text, parse_mode='Markdown')
        
    elif call.data == "guide_dca":
        guide_text = (
            "💰 *Dollar Cost Averaging*\n\n"
            "Spread your investment across multiple purchases.\n\n"
            "*Command:* `/dca <pair> <intervals> <total_amount>`\n"
            "*Example:* `/dca BTC/USDT 10 1000`\n\n"
            "This invests $1000 across 10 separate buys."
        )
        telegram_bot.send_message(chat_id, guide_text, parse_mode='Markdown')
        
    elif call.data == "show_balance":
        telegram_bot.send_message(
            chat_id, 
            "💵 *Check Balance*\n\nUse: `/balance <SYMBOL>`\n\nExample: `/balance USDT`",
            parse_mode='Markdown'
        )
        
    elif call.data == "show_portfolio":
        telegram_bot.send_message(
            chat_id, 
            "📈 Use `/portfolio` to view your total holdings in USDT."
        )
        
    elif call.data == "show_help":
        help_text = (
            "❓ *Available Commands*\n\n"
            "• `/grid` - Setup grid trading\n"
            "• `/dca` - Setup DCA strategy\n"
            "• `/balance` - Check token balance\n"
            "• `/portfolio` - View total portfolio\n"
            "• `/start` - Show main menu"
        )
        telegram_bot.send_message(chat_id, help_text, parse_mode='Markdown')


@telegram_bot.message_handler(commands=['grid'])
def handle_grid_command(message):
    """Handle grid trading setup command."""
    params = message.text.split()
    
    if len(params) != 5:
        error_msg = (
            "⚠️ *Invalid Format*\n\n"
            "Use: `/grid <pair> <levels> <min> <max>`\n"
            "Example: `/grid BTC/USDT 5 30000 35000`"
        )
        telegram_bot.reply_to(message, error_msg, parse_mode='Markdown')
        return
    
    try:
        pair = params[1]
        levels = int(params[2])
        min_price = float(params[3])
        max_price = float(params[4])
        
        grid_engine = GridTradingEngine(
            exchange=crypto_exchange,
            trading_pair=pair,
            num_levels=levels,
            price_floor=min_price,
            price_ceiling=max_price
        )
        grid_engine.place_grid_orders()
        
        telegram_bot.reply_to(
            message, 
            f"✅ Grid orders placed!\n\n📊 {levels} orders from ${min_price:,.0f} to ${max_price:,.0f}"
        )
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ Error: {str(e)}")


@telegram_bot.message_handler(commands=['dca'])
def handle_dca_command(message):
    """Handle DCA setup command."""
    params = message.text.split()
    
    if len(params) != 4:
        error_msg = (
            "⚠️ *Invalid Format*\n\n"
            "Use: `/dca <pair> <intervals> <amount>`\n"
            "Example: `/dca BTC/USDT 10 1000`"
        )
        telegram_bot.reply_to(message, error_msg, parse_mode='Markdown')
        return
    
    try:
        pair = params[1]
        intervals = int(params[2])
        total_amount = float(params[3])
        
        dca_engine = DollarCostAverager(
            exchange=crypto_exchange,
            trading_pair=pair,
            num_intervals=intervals,
            investment_amount=total_amount
        )
        dca_engine.execute_purchases()
        
        per_purchase = total_amount / intervals
        telegram_bot.reply_to(
            message, 
            f"✅ DCA orders placed!\n\n💰 ${per_purchase:,.2f} × {intervals} purchases"
        )
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ Error: {str(e)}")


@telegram_bot.message_handler(commands=['balance'])
def handle_balance_command(message):
    """Handle balance check command."""
    params = message.text.split()
    
    if len(params) != 2:
        telegram_bot.reply_to(
            message, 
            "⚠️ Use: `/balance <SYMBOL>`\nExample: `/balance USDT`",
            parse_mode='Markdown'
        )
        return
    
    token = params[1].upper()
    
    try:
        balance_info = crypto_exchange.fetch_token_balance(token)
        response = (
            f"💵 *{token} Balance*\n\n"
            f"Available: `{balance_info['available']}`\n"
            f"In Orders: `{balance_info['locked']}`\n"
            f"Total: `{balance_info['total']}`"
        )
        telegram_bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ Error: {str(e)}")


@telegram_bot.message_handler(commands=['portfolio'])
def handle_portfolio_command(message):
    """Handle portfolio value command."""
    try:
        total_value = crypto_exchange.calculate_portfolio_usdt()
        telegram_bot.reply_to(
            message, 
            f"📈 *Portfolio Value*\n\n💵 Total: `${total_value:,.2f} USDT`",
            parse_mode='Markdown'
        )
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🤖 AutoSwing Telegram Bot is running...")
    telegram_bot.infinity_polling()
