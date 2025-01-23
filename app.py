import os
import streamlit as st
import anthropic
import aiohttp
import asyncio
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_community.utilities import GoogleSearchAPIWrapper

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

google_search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
st.markdown("""
    <style>
        .streamlit-expanderHeader {
            text-align: right;
        }
        body {
            direction: rtl;
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True)

async def fetch_content_async(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    paragraphs = soup.find_all('p', limit=5)
                    return '\n'.join([p.get_text() for p in paragraphs])[:1500]  # الحد من النص
                else:
                    return f"❌ لم يتمكن من الوصول إلى {url} - حالة HTTP: {response.status}"
    except asyncio.TimeoutError:
        return f"⏳ انتهت مهلة الاتصال بالموقع: {url}"
    except Exception as e:
        return f"⚠️ خطأ أثناء جلب المحتوى من {url}: {e}"

async def fetch_all_content(urls):
    tasks = [fetch_content_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

st.title("مستشارك لتسويق منتجاتك بكل ذكاء")
st.markdown("أدخل تفاصيل منتجك، وبقدم لك نصائح بناء على السوق العربي لليوم")

product_name = st.text_input("أدخل اسم المنتج:")
product_description = st.text_area("أدخل وصف المنتج:")

if st.button("إرسال"):
    if product_name.strip() and product_description.strip():
        # st.write("⏳ جارٍ معالجة الاستفسار...")

        try:
            search_query = product_description

            with st.spinner("🔍  اقرأ لك السوق الأن ..."):
                search_results = google_search.results(search_query, num_results=10)

            urls = [result.get('link', '') for result in search_results]

            with st.spinner("📄 أحلل لك استراتجيات السوق.."):
                page_contents = asyncio.run(fetch_all_content(urls))

            formatted_content = "\n\n".join(page_contents)
            example_content = """
            🌟 تمر العجوة الفاخر - مذاق الأجداد بنكهة حديثة

            **الوصف:**
            تمتع بمذاق تمر العجوة الفاخر، المقطوف بعناية من مزارع المدينة المنورة. يتميز بنكهته الغنية وقيمته الغذائية العالية التي تجعله الخيار المثالي لمحبي التمور.

            **المميزات التنافسية:**
            - طبيعي 100% بدون إضافات
            - حاصل على شهادة الجودة السعودية
            - طعم فريد وقوام ناعم
            - متوفر بعبوات متنوعة تناسب جميع الأذواق
            - شحن سريع لجميع مناطق المملكة

            **الجمهور المستهدف:**
            - محبي التمور الفاخرة
            - المهتمون بالتغذية الصحية
            - الباحثون عن هدايا فاخرة

            **اقتراحات للحملات التسويقية:**
            1. **حملات موسمية:**
            - عروض شهر رمضان
            - باقات هدايا للأعياد والمناسبات

            2. **حملات رقمية:**
            - فيديوهات توعوية عن فوائد التمر
            - مشاركة وصفات صحية باستخدام المنتج

            **شعار الحملة:**
            "تمر العجوة – تراث أصيل، مذاق فريد"
            """

            marketing_prompt = f"""
            اعتمد على المثال التالي لإنشاء محتوى تسويقي مشابه للمنتج التالي، مع دراسة المحتوى المقدم واستنتاج استراتيجيات التسويق منه:

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
            
            
"يرجى التأكد من أن المحتوى يظهر بوضوح وبشكل منظم مع استخدام العناوين والقوائم لزيادة قابلية القراءة"
            """

            with st.spinner("📝 ..."):
                marketing_response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": marketing_prompt}]
                )
            formatted_text = marketing_response.content[0].text

            formatted_text = formatted_text.replace("\n\n", "\n")  
            st.markdown("### اقترح لك  :")
            st.markdown(formatted_text)
            # st.text_area(
            #     value=formatted_text , 
            #     height=500, 
            # )

            # marketing_prompt = f"استنادًا إلى المعلومات التالية، قم بإنشاء محتوى تسويقي احترافي يشمل:\n\n"
            # marketing_prompt += "- وصف جذاب للمنتج.\n"
            # marketing_prompt += "- فوائد تنافسية.\n"
            # marketing_prompt += "- الجمهور المستهدف.\n"
            # marketing_prompt += "- اقتراحات للحملات التسويقية.\n\n"
            # marketing_prompt += formatted_content

            # with st.spinner("📝 إنشاء المحتوى التسويقي..."):
            #     marketing_response = client.messages.create(
            #         model="claude-3-5-sonnet-20241022",
            #         max_tokens=1024,
            #         messages=[{"role": "user", "content": marketing_prompt}]
            #     )

            # st.success("✅ تمت العملية بنجاح")
            # st.markdown("### المحتوى التسويقي الناتج:")
            # # st.markdown(f"📄 {marketing_response.content.text if hasattr(marketing_response.content, 'text') else str(marketing_response.content)}")

            st.markdown("### المصادر المستخدمة:")
            for result in search_results:
                st.markdown(f"- [{result.get('title', 'عنوان غير متاح')}]({result.get('link', '#')})")

        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")
    else:
        st.warning("⚠ الرجاء إدخال اسم المنتج ووصفه قبل الضغط على إرسال")

st.markdown("---")
st.markdown("Sawq Team,2025")
