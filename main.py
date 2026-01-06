import os
import random
import datetime
import hashlib
import hmac
import qrcode
import json
import requests
import threading

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.clock import mainthread

# --- CONFIGURATION ---
# 1. Project ID (Extracted from your uploaded file)
FIREBASE_PROJECT_ID = vegetable-garden-aa4ef

# 2. YOU MUST PASTE YOUR WEB API KEY HERE
# Go to Firebase Console - Project Settings - General - Web API Key
FIREBASE_API_KEY = PASTE_YOUR_WEB_API_KEY_HERE

# Firestore REST API URL
FIRESTORE_URL = fhttpsfirestore.googleapis.comv1projects{FIREBASE_PROJECT_ID}databases(default)documentstransactions

SECRET_KEY = my_super_secret_server_key

# --- KIVY DESIGN (KV Language) ---
KV = '''
Screen
    MDBoxLayout
        orientation vertical
        padding 20dp
        spacing 15dp
        
        MDLabel
            text VEGETABLE GARDEN ADMIN
            halign center
            theme_text_color Custom
            text_color 0.23, 0.66, 0.35, 1
            font_style H5
            size_hint_y None
            height 50dp

        MDTextField
            id name_field
            hint_text Member Name
            mode rectangle

        MDTextField
            id amount_field
            hint_text Amount (PHP)
            mode rectangle
            input_filter float

        MDTextField
            id purpose_field
            hint_text Purpose (e.g. Sagada Tour)
            text Sagada Tour
            mode rectangle

        MDBoxLayout
            orientation horizontal
            spacing 10dp
            size_hint_y None
            height 60dp
            
            MDTextField
                id mode_field
                hint_text Mode (CashGCash)
                text Cash
                mode rectangle
            
            MDTextField
                id ref_field
                hint_text Ref No. (Optional)
                mode rectangle

        MDFillRoundFlatButton
            id gen_btn
            text GENERATE & SAVE
            md_bg_color 0.23, 0.66, 0.35, 1
            size_hint_x 1
            on_release app.start_generation_process()

        Image
            id qr_image
            source 
            size_hint_y 1
            allow_stretch True

        MDLabel
            id status_label
            text Ready...
            halign center
            theme_text_color Secondary
            font_style Caption
            size_hint_y None
            height 40dp
'''

class VGAdminApp(MDApp)
    def build(self)
        self.theme_cls.primary_palette = Green
        return Builder.load_string(KV)

    def start_generation_process(self)
        Starts the process in a background thread to keep UI responsive.
        name = self.root.ids.name_field.text.strip()
        amount = self.root.ids.amount_field.text.strip()
        purpose = self.root.ids.purpose_field.text.strip()
        mode = self.root.ids.mode_field.text.strip()
        manual_ref = self.root.ids.ref_field.text.strip()
        
        if not name or not amount
            self.root.ids.status_label.text = Error Name and Amount required!
            return

        # Disable button and update status
        self.root.ids.gen_btn.disabled = True
        self.root.ids.status_label.text = Processing...

        # Run logic in background
        threading.Thread(target=self.generate_qr_background, 
                         args=(name, amount, purpose, mode, manual_ref)).start()

    def generate_qr_background(self, name, amount, purpose, mode, manual_ref)
        receiver = Admin Mobile
        final_ref = manual_ref.upper() if manual_ref else CASH- + str(random.randint(1000, 9999))
        now = datetime.datetime.now()
        date_str = now.strftime(%m%d%y%H%M%S)

        # 1. Logic & Signature
        raw_data = f{name}{amount}{date_str}{mode}{receiver}{final_ref}{purpose}
        signature = hmac.new(SECRET_KEY.encode(), raw_data.encode(), hashlib.sha256).hexdigest()
        approval_code = signature[6].upper()

        # 2. Prepare Data for Firestore REST API
        # The REST API requires strict type definitions (stringValue, doubleValue, etc.)
        firestore_data = {
            fields {
                name {stringValue name},
                amount {doubleValue float(amount)},
                date {stringValue date_str},
                mode {stringValue mode},
                receiver {stringValue receiver},
                ref {stringValue final_ref},
                purpose {stringValue purpose},
                approvalCode {stringValue approval_code},
                status {stringValue PENDING},
                signature {stringValue signature},
                generatedAt {timestampValue datetime.datetime.utcnow().isoformat() + Z}
            }
        }

        # 3. Upload to Firestore via REST
        try
            # We use PATCH on a specific document ID to set the ID manually (same as .document(signature).set(...) in python)
            doc_url = f{FIRESTORE_URL}{signature}key={FIREBASE_API_KEY}
            
            # Perform the request
            response = requests.patch(doc_url, json=firestore_data)
            
            if response.status_code != 200
                # If it fails, show the error code
                error_msg = fAPI Error {response.status_code}
                try
                    error_detail = response.json().get('error', {}).get('message', '')
                    error_msg += f - {error_detail}
                except
                    pass
                self.update_ui_error(error_msg)
                return

            # 4. Generate QR Image (Only if upload success)
            final_string = f{raw_data}{signature}
            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(final_string)
            qr.make(fit=True)
            img = qr.make_image(fill_color=black, back_color=white)

            # Save to temp file
            filename = latest_qr.png
            img.save(filename)
            
            # Update UI (Must be done on main thread)
            self.update_ui_success(filename, approval_code)

        except Exception as e
            self.update_ui_error(fConnection Error {str(e)})

    @mainthread
    def update_ui_success(self, filename, code)
        self.root.ids.qr_image.source = filename
        self.root.ids.qr_image.reload()
        self.root.ids.status_label.text = fSuccess! Code {code}
        self.root.ids.gen_btn.disabled = False

    @mainthread
    def update_ui_error(self, message)
        self.root.ids.status_label.text = message
        self.root.ids.gen_btn.disabled = False

if __name__ == '__main__'
    VGAdminApp().run()