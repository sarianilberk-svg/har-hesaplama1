import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="UYAP Karar Asistanı V1.0", layout="wide")
st.title("⚖️ UYAP Karar Asistanı V1.0")
st.markdown("Hızlı Karar Hesaplama ve Hüküm Fıkrası Oluşturma Ekranı")

# Türk Lirası Formatlayıcı
def tr_format(miktar):
    return f"{miktar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 1. BÖLÜM: Veri Girişi
st.header("📝 1. Dava Bilgileri ve Masraflar")
col1, col2 = st.columns(2)

with col1:
    talep = st.number_input("Dava Değeri / Talep (TL)", min_value=0.0, value=100000.0, step=1000.0)
    kabul = st.number_input("Kabul Edilen Tutar (TL)", min_value=0.0, value=60000.0, step=1000.0)
    pesin_harc = st.number_input("Yatan Peşin + Islah Harcı (TL)", min_value=0.0, value=1707.75, step=10.0)

    if kabul > talep:
        st.error("Kabul edilen tutar, dava değerinden büyük olamaz!")
        kabul = talep

with col2:
    basvuru = st.number_input("Başvurma Harcı (TL)", min_value=0.0, value=732.0, step=10.0)
    d_gider = st.number_input("Davacı Harç Dışı Gideri (TL)", min_value=0.0, value=5000.0, step=100.0)
    dv_gider = st.number_input("Davalı Harç Dışı Gideri (TL)", min_value=0.0, value=0.0, step=100.0)

# 2. BÖLÜM: Hesaplamalar
reddedilen = talep - kabul
kabul_orani = kabul / talep if talep > 0 else 0
ret_orani = reddedilen / talep if talep > 0 else 0

alinmasi_gereken_harc = max(kabul * (68.31 / 1000), 732.0)
bakiye_harc = alinmasi_gereken_harc - pesin_harc
iade_harc = 0.0

if bakiye_harc < 0:
    iade_harc = abs(bakiye_harc)
    bakiye_harc = 0.0

d_gider_davali_payi = d_gider * kabul_orani
dv_gider_davaci_payi = dv_gider * ret_orani

st.divider()

# 3. BÖLÜM: Hüküm Metni Oluşturma
st.header("📜 2. Otomatik Hüküm Fıkrası")
st.markdown("Aşağıdaki metni seçerek kopyalayabilir ve UYAP'a doğrudan yapıştırabilirsiniz.")

hukum = "HÜKÜM: Gerekçesi ekli kararda açıklanacağı üzere;\n\n"

if kabul == talep:
    hukum += f"**1-** Davanın KABULÜNE, {tr_format(kabul)} TL'nin davalıdan alınarak davacıya VERİLMESİNE,\n\n"
else:
    hukum += f"**1-** Davanın KISMEN KABULÜNE, KISMEN REDDİNE;\n"
    hukum += f"&nbsp;&nbsp;&nbsp;&nbsp;**a)** {tr_format(kabul)} TL'nin davalıdan alınarak davacıya VERİLMESİNE,\n"
    hukum += f"&nbsp;&nbsp;&nbsp;&nbsp;**b)** Fazlaya ilişkin {tr_format(reddedilen)} TL'lik talebin REDDİNE,\n\n"

hukum += f"**2-** Karar tarihinde yürürlükte bulunan Harçlar Tarifesi gereğince, alınması gereken {tr_format(alinmasi_gereken_harc)} TL nispi karar ve ilam harcından, davacı tarafından peşin yatırılan {tr_format(pesin_harc)} TL harcın mahsubu ile bakiye {tr_format(bakiye_harc)} TL harcın DAVALIDAN ALINARAK HAZİNE'YE İRAT KAYDINA,\n\n"

if iade_harc > 0:
    hukum += f"**-** Mahsup sonrası fazla yatırıldığı anlaşılan {tr_format(iade_harc)} TL harcın karar kesinleştiğinde istek halinde DAVACIYA İADESİNE,\n\n"

hukum += f"**3-** Davacı tarafından yatırıldığı anlaşılan {tr_format(pesin_harc)} TL karar-ilam harcı ile {tr_format(basvuru)} TL başvurma harcı toplamı olan {tr_format(pesin_harc + basvuru)} TL harcın DAVALIDAN ALINARAK DAVACIYA VERİLMESİNE,\n\n"

hukum += f"**4-** Davacı tarafından yapılan harç dışı toplam {tr_format(d_gider)} TL yargılama giderinden haklılık oranına isabet eden {tr_format(d_gider_davali_payi)} TL'nin DAVALIDAN ALINARAK DAVACIYA VERİLMESİNE, bakiye kısmın davacı üzerinde BIRAKILMASINA,\n\n"

if dv_gider > 0:
    hukum += f"**5-** Davalı tarafından yapılan harç dışı toplam {tr_format(dv_gider)} TL yargılama giderinden haklılık oranına isabet eden {tr_format(dv_gider_davaci_payi)} TL'nin DAVACIDAN ALINARAK DAVALIYA VERİLMESİNE, bakiye kısmın davalı üzerinde BIRAKILMASINA,\n\n"
else:
    hukum += f"**5-** Davalı tarafından yapılan yargılama gideri bulunmadığından bu hususta karar verilmesine YER OLMADIĞINA,\n\n"

hukum += "**6-** Davacı yararına AAÜT gereğince hesaplanan ... TL vekalet ücretinin DAVALIDAN ALINARAK DAVACIYA VERİLMESİNE,\n\n"

if reddedilen > 0:
    hukum += "**7-** Davalı yararına AAÜT gereğince hesaplanan ... TL vekalet ücretinin DAVACIDAN ALINARAK DAVALIYA VERİLMESİNE,\n\n"

hukum += "**8-** Taraflarca yatırılan gider avansından kullanılmayan kısmın karar kesinleştiğinde HMK m.333 uyarınca yatırana İADESİNE karar verildi."

st.info(hukum)
