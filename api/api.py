from quart import Quart, request, jsonify
from datetime import datetime, timedelta

from src.database.models import User

# --------------------------- #

app = Quart(__name__)

# --------------------------- #

@app.route('/subscribe', methods=['POST'])
async def subscribe():
    data = await request.get_json()
    chat_id = data.get('chat_id')
    days_to_add = data.get('days')

    if not chat_id or not days_to_add:
        return jsonify({"error": "CHAT_ID and DAYS are required"}), 400

    try:
        # پیدا کردن تاریخ منقضی شدن فعلی
        user = User.get(User.user_id == chat_id)
        current_expiry_timestamp = user.datetime_subscription

        # تبدیل timestamp به تاریخ و افزودن روزها
        current_expiry_date = datetime.utcfromtimestamp(current_expiry_timestamp)
        new_expiry_date = current_expiry_date + timedelta(days=days_to_add)

        # تبدیل تاریخ جدید به timestamp
        new_expiry_timestamp = int(new_expiry_date.timestamp())

        # آپدیت کردن تاریخ اشتراک
        User.update(datetime_subscription=new_expiry_timestamp).where(User.user_id == chat_id).execute()

        return jsonify({"message": "Subscription updated successfully", "expiry_date": new_expiry_date.strftime('%Y-%m-%d')}), 200

    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
