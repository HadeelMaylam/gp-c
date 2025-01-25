import os
import streamlit as st
import openai
import requests
import anthropic
from gtts import gTTS
from io import BytesIO

from dotenv import load_dotenv

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from langchain_community.utilities import GoogleSearchAPIWrapper

##############################
# تهيئة المفاتيح والـ API
##############################
load_dotenv()  # تحميل المتغيرات من ملف .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
google_search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

##############################
# إعداد واجهة الصفحة الافتراضية
##############################
st.set_page_config(page_title="سوّق", layout="centered")

##############################
# ضبط اتجاه النصوص إلى اليمين
##############################
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
        background-color: #ffffff !important;
        color: #000000;
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
    .streamlit-expanderHeader {
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

##############################
# استخدام حالة الجلسة للتنقل
##############################
if "page" not in st.session_state:
    st.session_state.page = "home"

##################################################################
# الصفحة الأولى: الصفحة الرئيسية (Home) مع عرض الشعار والأزرار
##################################################################
def home_page():
    st.image("logo.pNg", width=1000)  # غيّر هذا المسار إن كان يختلف اسم الملف أو مكانه
    st.title("سوّق")
    st.markdown("### أداة تعمل بتقنيات الذكاء الاصطناعي لإنشاء محتوى تسويقي جذاب خلال ثواني")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("مستشارك التسويقي الذكي"):
            st.session_state.page = "marketing_advisor"  # الانتقال لصفحة التحليل
            st.rerun()

    with col2:
        if st.button("كتابة محتوى نصي"):
            st.session_state.page = "text_content"       # الانتقال لصفحة المحتوى النصي
            st.rerun()

    with col3:
        if st.button("تصميم علامة تجارية"):
            st.session_state.page = "brand_design"       # الانتقال لصفحة تصميم الشعار
            st.rerun()

##################################################################
# مثال لصفحة تصميم العلامة التجارية (brand_design)
##################################################################
def brand_design_page():
    st.title("توليد علامة تجارية")

    product_name = st.text_input("أدخل اسم المنتج أو العلامة التجارية:")
    style_choice = st.radio(
        "اختر نوع الشعار:",
        options=["شعار نصي", "شعار حرفي", "شعار رمزي", "شخصية", "لا شيء"],
        horizontal=True
    )
    description = st.text_area("أدخل وصفًا إضافيًا للشعار:")

    if st.button("توليد الشعار"):
        if product_name and style_choice != "لا شيء":
            prompt = generate_logo_prompt(product_name, style_choice, description)
            file_path = generate_image(prompt)
            if file_path:
                st.image(file_path, caption="الشعار المولد باستخدام DALL-E")
                st.success(f"تم حفظ الشعار في المسار: {file_path}")
            else:
                st.error("حدث خطأ أثناء توليد الشعار. حاول مرة أخرى.")
        else:
            st.warning("يرجى إدخال اسم المنتج واختيار نوع الشعار.")

def generate_logo_prompt(product_name, style_choice, description):
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

def generate_image(prompt):
    """توليد صورة باستخدام DALL-E"""
    try:
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

##################################################################
# مثال لصفحة كتابة المحتوى النصي (text_content)
# (نفس فكرة marketing_content_section في الكود السابق)
##################################################################
def text_content_page():
    st.title("معلومات المحتوى التسويقي")

    comments = st.text_area("أضف تفاصيل حوّل منتجك هنا:")
    content_types = [
        "نشر خبر", "إعلان نصي", "سرد قصصي",
        "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"
    ]
    content_type = st.selectbox("اختر نوع المحتوى التسويقي:", content_types)
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("توصيه لاختيار نوع المحتوى التسويقي"):
            if comments:
                recommended_type = get_recommended_marketing_type(comments, content_types)
                st.success(f"التوصية: أفضل نوع تسويقي لمنتجك هو '{recommended_type}'")
            else:
                st.warning("يرجى إدخال وصف المنتج للحصول على التوصية.")

    with col2:
        if st.button("توليد النص التسويقي"):
            if marketing_field and target_audience:
                summary_message = f"""
                النتائج:
                - وصف المنتج: {comments if comments else 'لم يتم إدخال وصف'}
                - مجال التسويق: {marketing_field if marketing_field else 'غير محدد'}
                - الجمهور المستهدف: {', '.join(target_audience) if target_audience else 'غير محدد'}
                - نوع المحتوى التسويقي: {content_type if content_type else 'غير محدد'}
                - المناسبة: {event if event and event != 'لا شيء' else 'لا توجد مناسبة محددة'}
                """
                st.markdown(summary_message)

                bot_response = model_text(marketing_field, target_audience, content_type, event, comments)
                st.text_area("النص التسويقي المولد:", value=bot_response, height=200)
            else:
                st.warning("يرجى تحديد مجال التسويق والجمهور المستهدف.")

def get_recommended_marketing_type(description, content_options):
    prompt = (
        f"أنت خبير في التسويق، بناءً على وصف المنتج التالي، "
        f"اختر أفضل نوع تسويق يناسبه من القائمة المقدمة:\n"
        f"وصف المنتج: {description}\n"
        f"الخيارات المتاحة: {', '.join(content_options)}\n"
        f"يرجى تقديم النوع الأنسب فقط دون تفاصيل إضافية."
    )
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        if response and hasattr(response, 'content'):
            return response.content[0].text.strip()
        else:
            return "تعذر تحديد النوع المناسب، الرجاء التحقق من المدخلات."
    except Exception as e:
        return f"حدث خطأ أثناء التوصية: {e}"

def model_text(marketing_field, target_audience, content_type, event, comments):
    user_message = (
        f"أجب كخبير تسويق. هدفك إنشاء نص تسويقي جذاب. "
        f"- مجال التسويق: {marketing_field}\n"
        f"- الجمهور المستهدف: {', '.join(target_audience) if target_audience else 'غير محدد'}\n"
        f"- نوع المحتوى التسويقي: {content_type}\n"
        f"- المناسبة: {event if event != 'لا شيء' else 'لا توجد مناسبة'}\n"
        f"- الملاحظات: {comments if comments else 'لا توجد ملاحظات'}\n"
    )
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}]
        )
        if response and hasattr(response, 'content'):
            return response.content[0].text
        else:
            return "تعذر توليد النص التسويقي."
    except Exception as e:
        return f"حدث خطأ أثناء توليد النص باستخدام Claude: {e}"

##################################################################
# صفحة مستشارك التسويقي الذكي (marketing_advisor)
# تحليل المحتوى من خلال البحث في جوجل + Claude
##################################################################
def marketing_advisor_page():
    st.title("مستشارك لتسويق منتجاتك بكل ذكاء")
    st.markdown("أدخل تفاصيل منتجك، وبقدم لك نصائح بناء على السوق العربي لليوم")

    product_name = st.text_input("أدخل اسم المنتج:")
    product_description = st.text_area("أدخل وصف المنتج:")

    if st.button("إرسال"):
        if product_name.strip() and product_description.strip():
            try:
                search_query = product_description

                with st.spinner("🔍  اقرأ لك السوق الآن ..."):
                    search_results = google_search.results(search_query, num_results=10)

                # جلب الروابط من نتائج البحث
                urls = [result.get('link', '') for result in search_results]

                with st.spinner("📄 أحلل لك استراتجيات السوق.."):
                    # تشغيل الجلب غير المتزامن للروابط
                    page_contents = asyncio.run(fetch_all_content(urls))

                formatted_content = "\n\n".join(page_contents)

                # مثال توضيحي للاعتماد عليه في بناء النموذج
                example_content = """
                🌟 تمر العجوة الفاخر - مذاق الأجداد بنكهة حديثة

                **الوصف:**
                تمتع بمذاق تمر العجوة الفاخر، المقطوف بعناية من مزارع المدينة المنورة. يتميز بنكهته الغنية وقيمته الغذائية العالية.

                **المميزات التنافسية:**
                - طبيعي 100% بدون إضافات
                - حاصل على شهادة الجودة السعودية
                - طعم فريد وقوام ناعم
                - شحن سريع لجميع مناطق المملكة

                **الجمهور المستهدف:**
                - محبي التمور الفاخرة
                - المهتمون بالتغذية الصحية
                - الباحثون عن هدايا فاخرة

                **اقتراحات للحملات التسويقية:**
                1. **حملات موسمية:** عروض شهر رمضان
                2. **حملات رقمية:** فيديوهات عن فوائد التمر
                **شعار الحملة:** تمر العجوة – تراث أصيل، مذاق فريد
                """

                marketing_prompt = f"""
                اعتمد على المثال التالي لإنشاء محتوى تسويقي مشابه للمنتج التالي، 
                مع دراسة المحتوى المقدم واستنتاج استراتيجيات التسويق منه:

                **مثال:**
                {example_content}

                **المحتوى المستخرج من الإنترنت:**
                {formatted_content}

                **المطلوب:**
                - تحليل المحتوى المقدم واستخراج الاستراتيجيات التسويقية منه.
                - إنشاء محتوى تسويقي يشمل:
                  - وصف جذاب للمنتج.
                  - فوائد تنافسية.
                  - الجمهور المستهدف.
                  - اقتراحات للحملات التسويقية.
                  - شعار مناسب.

                يرجى التأكد من أن المحتوى يظهر بوضوح وبشكل منظم مع استخدام العناوين والقوائم.
                """

                with st.spinner("📝 جاري توليد المحتوى ..."):
                    marketing_response = anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": marketing_prompt}]
                    )

                if marketing_response and hasattr(marketing_response, 'content'):
                    formatted_text = marketing_response.content[0].text
                else:
                    formatted_text = "تعذر جلب الاستجابة من Claude."

                # تحسين تنسيق النص
                formatted_text = formatted_text.replace("\n\n", "\n")

                st.markdown("### اقترح لك:")
                st.markdown(formatted_text)

                st.markdown("### المصادر المستخدمة:")
                for result in search_results:
                    link = result.get('link', '#')
                    title = result.get('title', 'عنوان غير متاح')
                    if link and link != '#':
                        st.markdown(f"- [{title}]({link})")

            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")
        else:
            st.warning("⚠ الرجاء إدخال اسم المنتج ووصفه قبل الضغط على إرسال")

    st.markdown("---")
    st.markdown("Sawq Team, 2025")

async def fetch_content_async(url):
    """جلب محتوى الصفحات بشكل غير متزامن (Async)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # نجلب 5 فقرات فقط
                    paragraphs = soup.find_all('p', limit=5)
                    return '\n'.join([p.get_text() for p in paragraphs])[:1500]
                else:
                    return f"❌ لم يتمكن من الوصول إلى {url} - حالة HTTP: {response.status}"
    except asyncio.TimeoutError:
        return f"⏳ انتهت مهلة الاتصال بالموقع: {url}"
    except Exception as e:
        return f"⚠️ خطأ أثناء جلب المحتوى من {url}: {e}"

async def fetch_all_content(urls):
    tasks = [fetch_content_async(url) for url in urls if url]
    results = await asyncio.gather(*tasks)
    return results

########################################
# توجيه الصفحات بناءً على session_state
########################################
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "marketing_advisor":
    marketing_advisor_page()
elif st.session_state.page == "text_content":
    text_content_page()
elif st.session_state.page == "brand_design":
    brand_design_page()
