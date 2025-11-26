# backend/app/utils/i18n.py
from typing import Dict, Any, Optional
from fastapi import Request

# 簡單的翻譯字典
# 實際應用中，這些內容會從 JSON 或 PO 檔案中載入
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "invalid_credentials": "Incorrect username or password",
        "inactive_user": "Inactive user",
        "user_already_registered": "Username already registered",
        "failed_to_send_verification_email": "Registration successful, but failed to send verification email. Please contact support.",
        "invalid_or_expired_verification_token": "Invalid or expired verification token.",
        "email_verified_successfully": "Email verified successfully. Your account is now active.",
        "password_reset_link_sent": "If an account with that email exists, a password reset link has been sent.",
        "failed_to_generate_password_reset_token": "Failed to generate password reset token.",
        "failed_to_send_password_reset_email": "Failed to send password reset email. Please contact support.",
        "new_password_and_confirmation_do_not_match": "New password and confirmation do not match.",
        "invalid_or_expired_password_reset_token": "Invalid or expired password reset token.",
        "password_has_been_reset_successfully": "Password has been reset successfully.",
        "rate_limit_exceeded": "Rate limit exceeded: {detail}",
        "invalid_file_type": "Invalid file type. Only images are allowed.",
        "file_not_valid_image_format": "File is not a valid image format.",
        "could_not_save_image_file": "Could not save image file.",
        "invalid_base64_string": "Invalid Base64 string.",
        "decoded_data_not_valid_image_format": "Decoded data is not a valid image format.",
        "could_not_save_image_from_base64_data": "Could not save image from Base64 data.",
        "failed_to_upload_signature": "Failed to upload signature: {detail}",
        "failed_to_upload_item_photo": "Failed to upload item photo for '{item_name}': {detail}",
        "user_not_linked_to_student_record": "User is not linked to a student record.",
        "already_have_active_inspection": "You already have an active inspection. Please wait for it to be processed.",
        "student_not_assigned_to_bed": "Student is not assigned to a bed.",
        "student_bed_not_assigned_to_room": "Student's bed is not assigned to a room.",
        "inspection_record_not_found": "Inspection record not found",
        "not_authorized_to_view_this_record": "Not authorized to view this record",
        "not_authorized_to_export_this_record": "Not authorized to export this record",
        "not_authorized_to_email_this_record": "Not authorized to email this record",
        "invalid_filename": "Invalid filename.",
        "invalid_filename_format": "Invalid filename format.",
        "image_not_found": "Image not found.",
        "image_record_corrupted_or_incomplete": "Image record is corrupted or incomplete.",
        "you_do_not_have_permission_to_access_this_image": "You do not have permission to access this image.",
        "image_file_not_found_on_disk": "Image file not found on disk.",
        "invalid_filename_path_traversal_detected": "Invalid filename, path traversal attempt detected.",
        "the_user_does_not_have_the_required_permission": "The user does not have the required '{permission}' permission",
        "could_not_validate_credentials": "Could not validate credentials",
        "not_authenticated": "Not authenticated",
        "failed_to_register_user": "Failed to register user: {detail}"
    },
    "zh": {
        "invalid_credentials": "使用者名稱或密碼不正確",
        "inactive_user": "非活躍使用者",
        "user_already_registered": "使用者名稱已被註冊",
        "failed_to_send_verification_email": "註冊成功，但未能發送驗證郵件。請聯絡支援。",
        "invalid_or_expired_verification_token": "無效或過期的驗證令牌。",
        "email_verified_successfully": "電子郵件驗證成功。您的帳戶現已啟用。",
        "password_reset_link_sent": "如果該電子郵件帳戶存在，已發送密碼重設連結。",
        "failed_to_generate_password_reset_token": "未能生成密碼重設令牌。",
        "failed_to_send_password_reset_email": "未能發送密碼重設郵件。請聯絡支援。",
        "new_password_and_confirmation_do_not_match": "新密碼與確認密碼不符。",
        "invalid_or_expired_password_reset_token": "無效或過期的密碼重設令牌。",
        "password_has_been_reset_successfully": "密碼已成功重設。",
        "rate_limit_exceeded": "請求頻率過高：{detail}",
        "invalid_file_type": "無效的檔案類型。只允許圖片。",
        "file_not_valid_image_format": "檔案不是有效的圖片格式。",
        "could_not_save_image_file": "無法儲存圖片檔案。",
        "invalid_base64_string": "無效的 Base64 字串。",
        "decoded_data_not_valid_image_format": "解碼後的數據不是有效的圖片格式。",
        "could_not_save_image_from_base64_data": "無法從 Base64 數據儲存圖片。",
        "failed_to_upload_signature": "簽名上傳失敗：{detail}",
        "failed_to_upload_item_photo": "項目圖片 '{item_name}' 上傳失敗：{detail}",
        "user_not_linked_to_student_record": "使用者未連結到學生記錄。",
        "already_have_active_inspection": "您已有一個活躍的檢查。請等待處理。",
        "student_not_assigned_to_bed": "學生未分配床位。",
        "student_bed_not_assigned_to_room": "學生的床位未分配到房間。",
        "inspection_record_not_found": "檢查記錄未找到",
        "not_authorized_to_view_this_record": "無權查看此記錄",
        "not_authorized_to_export_this_record": "無權匯出此記錄",
        "not_authorized_to_email_this_record": "無權發送此記錄的電子郵件",
        "invalid_filename": "無效的檔名。",
        "invalid_filename_format": "無效的檔名格式。",
        "image_not_found": "圖片未找到。",
        "image_record_corrupted_or_incomplete": "圖片記錄已損壞或不完整。",
        "you_do_not_have_permission_to_access_this_image": "您沒有權限存取此圖片。",
        "image_file_not_found_on_disk": "圖片檔案在磁碟上未找到。",
        "invalid_filename_path_traversal_detected": "無效檔名，檢測到路徑遍歷嘗試。",
        "the_user_does_not_have_the_required_permission": "使用者沒有所需的 '{permission}' 權限",
        "could_not_validate_credentials": "無法驗證憑證",
        "not_authenticated": "未驗證",
        "failed_to_register_user": "註冊使用者失敗：{detail}"
    }
}

DEFAULT_LANGUAGE = "zh" # 預設語言為繁體中文

def get_locale_from_request(request: Request) -> str:
    """
    從 Request 的 Accept-Language header 中獲取最佳匹配的語言。
    """
    accept_language = request.headers.get("Accept-Language")
    if accept_language:
        # 解析 Accept-Language header (例如: "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")
        # 簡單的實現：只取第一個語言
        preferred_language = accept_language.split(',')[0].lower().strip()
        if preferred_language.startswith("zh"): # 匹配所有中文變體
            return "zh"
        elif preferred_language.startswith("en"): # 匹配所有英文變體
            return "en"
    return DEFAULT_LANGUAGE

def _(key: str, request: Optional[Request] = None, **kwargs: Any) -> str:
    """
    翻譯函式。
    如果提供了 request，則根據 Accept-Language header 進行翻譯。
    否則使用預設語言。
    支援字串格式化。
    """
    lang = DEFAULT_LANGUAGE
    if request:
        lang = get_locale_from_request(request)
    
    translated_message = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)
    return translated_message.format(**kwargs)

# 為了方便在 FastAPI 中使用，我們可以創建一個依賴項
async def get_translate_function(request: Request) -> callable:
    """
    提供一個可以根據當前請求語言進行翻譯的函式。
    """
    lang = get_locale_from_request(request)
    def translate_func(key: str, **kwargs: Any) -> str:
        translated_message = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)
        return translated_message.format(**kwargs)
    return translate_func

# 將 _ 函式暴露，以便在沒有 request 的情況下使用預設語言翻譯
__ = _
