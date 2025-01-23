import os
import streamlit as st
import anthropic
import openai
import requests
from gtts import gTTS
from io import BytesIO

class SouqApp:
    def __init__(self):
        self.setup_page_config()
        self.setup_custom_styles()
        self.openai_api_key = st.secrets["api_keys"]["openai_api_key"]
        self.anthropic_api_key = st.secrets["api_keys"]["anthropic_api_key"]
        self.client = anthropic.Client(api_key=self.anthropic_api_key)

    def setup_page_config(self):
        """إعداد إعدادات الصفحة"""
        st.set_page_config(page_title="سوّق", layout="centered")

    def setup_custom_styles(self):
        """إضافة أنماط CSS مخصصة"""
        st.markdown(
            """
            <style>
            body {
                direction: rtl;
                text-align: right;
            }
            .stButton > button {
                direction: rtl;
            }
            .stTextInput > div > div {
                text-align: right;
            }
            .stRadio > div {
                direction: rtl;
            }
            .stTextArea > label {
                text-align: right;
            }
            .stSelectbox > label {
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    def home_page(self):
        """الصفحة الرئيسية"""
        st.write("\n\n أهلاً بك في منصة سوق")

    def brand_section(self):
        """قسم العلامة التجارية"""
        st.title("توليد علامة تجارية")

        with st.form(key="brand_form"):
            product_name = st.text_input("أدخل اسم المنتج أو العلامة التجارية:")
            style_choice = st.radio(
                "اختر نوع الشعار:",
                options=["شعار نصي", "شعار حرفي", "شعار رمزي", "شخصية", "لا شيء"],
                horizontal=True
            )
            description = st.text_area("أدخل وصفًا إضافيًا للشعار:")

            submitted = st.form_submit_button("توليد الشعار")
            if submitted:
                if product_name and style_choice != "لا شيء":
                    prompt = self.generate_logo_prompt(product_name, style_choice, description)
                    file_path = self.generate_image(prompt)
                    if file_path:
                        st.image(file_path, caption="الشعار المولد باستخدام DALL-E 3")
                        st.success(f"تم حفظ الشعار في المسار: {file_path}")
                    else:
                        st.error("حدث خطأ أثناء توليد الشعار. حاول مرة أخرى.")
                else:
                    st.warning("يرجى إدخال اسم المنتج واختيار نوع الشعار.")

    def generate_logo_prompt(self, product_name, style_choice, description):
        """إنشاء نص لطلب تصميم الشعار"""
        if style_choice == "شعار نصي":
            return (
                f"Design a clean and elegant text-based logo for the brand '{product_name}'. "
                f"The logo should focus on text with a sleek and readable style. {description if description else ''}"
            )
        elif style_choice == "شعار حرفي":
            return (
                f"Create a professional logo using the initials of the brand name '{product_name}'. "
                f"The design should reflect the identity of the brand. {description if description else ''}"
            )
        elif style_choice == "شعار رمزي":
            return (
                f"Design a unique symbolic logo for the brand '{product_name}'. "
                f"Use icons or symbols that represent the concept of the brand effectively. {description if description else ''}"
            )
        elif style_choice == "شخصية":
            return (
                f"Create a character-based logo representing the brand '{product_name}'. "
                f"The character should be unique and visually aligned with the brand's identity. {description if description else ''}"
            )
        else:
            return (
                f"Design an innovative logo for the product or brand named '{product_name}'. {description if description else ''}"
            )

    def generate_image(self, prompt):
        """توليد صورة باستخدام DALL-E"""
        try:
            openai.api_key = self.openai_api_key
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']

            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                os.makedirs("images", exist_ok=True)
                file_path = os.path.join("images", "generated_logo.png")
                with open(file_path, "wb") as file:
                    file.write(image_response.content)
                return file_path
            else:
                st.error("فشل في تحميل الصورة من الرابط.")
                return None
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
            return None

    def marketing_content_section(self):
        """قسم المحتوى التسويقي"""
        st.title("معلومات المحتوى التسويقي")

        with st.form(key="marketing_form"):
            comments = st.text_area("أضف تفاصيل حوّل منتجك هنا:")
            submit_button = st.form_submit_button("توصيه لاختيار نوع المحتوى التسويقي")

            content_types = [
                "نشر خبر", "إعلان نصي", "سرد قصصي",
                "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"
            ]

            content_type = st.selectbox(
                "اختر نوع المحتوى التسويقي:",
                content_types
            )

            if content_type == "أخرى":
                custom_content_type = st.text_input("أدخل نوع المحتوى التسويقي:")
                content_type = custom_content_type if custom_content_type else None

            event = st.selectbox(
                "اختر المناسبة التي تريد التسويق لها:",
                ["يوم وطني", "عيد فطر", "عيد أضحى", "رمضان", "يوم التأسيس", "العطلة", "أخرى", "لا شيء"]
            )

            if event == "أخرى":
                custom_event = st.text_input("أدخل المناسبة:")
                event = custom_event if custom_event else None

            marketing_field = st.selectbox(
                "اختر مجال التسويق",
                ["التسويق الرقمي", "التسويق التقليدي", "تسويق المحتوى",
                 "التسويق عبر السوشيال ميديا", "التسويق عبر البريد الإلكتروني", "أخرى"]
            )

            if marketing_field == "أخرى":
                custom_marketing_field = st.text_input("*أدخل مجال التسويق:")
                marketing_field = custom_marketing_field if custom_marketing_field else None

            target_audience = st.multiselect(
                "*اختر الجمهور المستهدف",
                ["الشركات", "الأفراد", "الشباب", "الأطفال", "الآباء",
                 "المهتمون بالتكنولوجيا", "المستثمرون", "أخرى"]
            )

            if "أخرى" in target_audience:
                custom_target_audience = st.text_input("أدخل جمهورًا مستهدفًا إضافيًا:")
                if custom_target_audience:
                    target_audience = [audience for audience in target_audience if audience != "أخرى"] + [custom_target_audience]

            if submit_button:
                if comments:
                    recommended_type = self.get_recommended_marketing_type(comments, content_types)
                    st.success(f"التوصية: أفضل نوع تسويقي لمنتجك هو '{recommended_type}'")
                else:
                    st.warning("يرجى إدخال وصف المنتج للحصول على التوصية.")

            submitted = st.form_submit_button("أرسل لسوّق")
            if submitted:
                if marketing_field and target_audience:
                    summary_message = f"""
                    النتائج:
                    - وصف المنتج: {comments if comments else 'لم يتم إدخال وصف'}
                    - مجال التسويق: {marketing_field if marketing_field else 'غير محدد'}
                    - الجمهور المستهدف: {', '.join(target_audience) if target_audience else 'غير محدد'}
                    - نوع المحتوى التسويقي: {content_type if content_type else 'يرجى إدخال نوع المحتوى التسويقي'}
                    - المناسبة: {event if event and event != 'لا شيء' else 'لا توجد مناسبة محددة'}
                    """
                    st.markdown(summary_message)

                    bot_response = self.model_text(marketing_field, target_audience, content_type, event, comments)
                    st.text_area("النص التسويقي المولد:", value=bot_response, height=200)

    def get_recommended_marketing_type(self, description, content_options):
        """الحصول على التوصية بنوع المحتوى التسويقي"""
        prompt = (
            f"أنت خبير في التسويق، بناءً على وصف المنتج التالي، قم باختيار أفضل نوع تسويق يناسبه من القائمة المقدمة:\n"
            f"وصف المنتج: {description}\n"
            f"الخيارات المتاحة: {', '.join(content_options)}\n"
            f"يرجى تقديم النوع الأنسب فقط دون تفاصيل إضافية."
        )

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )

            if response and response.content:
                return response.content[0].text.strip()
            else:
                return "تعذر تحديد النوع المناسب، الرجاء التحقق من المدخلات."
        except Exception as e:
            return f"حدث خطأ أثناء التوصية: {e}"

    def model_text(self, marketing_field, target_audience, content_type, event, comments):
        """توليد نص تسويقي باستخدام Claude-3"""
        user_message = (
            f"أجب على أساس أنك خبير تسويق محترف وهدفك هو إنشاء نص تسويقي يجذب الجمهور المستهدف ويحقق أهداف العميل. بناءً على الاختيارات التالية:\n"
            f"- مجال التسويق: {marketing_field}\n"
            f"- الجمهور المستهدف: {', '.join(target_audience) if target_audience else 'غير محدد'}\n"
            f"- نوع المحتوى التسويقي: {content_type}\n"
            f"- المناسبة: {event if event != 'لا شيء' else 'لا توجد مناسبة'}\n"
            f"- الملاحظات: {comments if comments else 'لا توجد ملاحظات'}\n"
            f"تأكد من أن النص الناتج يكون مبتكرًا ومقنعًا، ومبنيًا على أفضل ممارسات التسويق."
        )

        try:
            messages = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": user_message}]
            )

            if messages and messages.content:
                return messages.content[0].text
            else:
                return (
                    f"نص تسويقي لمجال {marketing_field} لجمهور {', '.join(target_audience)} "
                    f"بمناسبة {event if event else 'لا توجد مناسبة محددة'}: {comments}"
                )
        except Exception as e:
            return (
                f"حدث خطأ أثناء توليد النص باستخدام Claude: {e}\n\n"
                f"نص تسويقي لمجال {marketing_field} لجمهور {', '.join(target_audience)} "
                f"بمناسبة {event if event else 'لا توجد مناسبة محددة'}: {comments}"
            )

    def run(self):
        """تشغيل التطبيق"""
        st.markdown(
            """
            <h1 style="text-align: right;">سوق لمنتجاتك مع سوّق</h1>
            """,
            unsafe_allow_html=True
        )

        menu = ["الرئيسية", "علامة تجارية", "محتوى تسويقي"]
        choice = st.sidebar.selectbox("", menu)

        if choice == "الرئيسية":
            self.home_page()
        elif choice == "علامة تجارية":
            self.brand_section()
        elif choice == "محتوى تسويقي":
            self.marketing_content_section()

if __name__ == "__main__":
    app = SouqApp()
    app.run()
