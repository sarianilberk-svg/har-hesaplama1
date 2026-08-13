import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="UYAP Karar Asistanı V1.1", layout="wide")
st.title("⚖️ UYAP Karar Asistanı V1.1")
st.markdown("Hızlı Karar Hesaplama, Hüküm Fıkrası ve **AAÜT Vekalet Ücreti** Modülü")

# Türk Lirası Formatlayıcı
def tr_format(miktar):
    return f"{miktar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# AAÜT Vekalet Ücreti Hesaplama Fonksiyonu (Excel'deki Kademeli Mantık)
def hesapla_vekalet(miktar):
    if miktar <= 0:
        return 0.0
    
    ucret = 0.0
    if miktar <= 600000:
        ucret = miktar * 0.16
    elif miktar <= 1200000:
        ucret = 96000 + (miktar - 600000) * 0.15
    elif miktar <= 2400000:
        ucret = 186000 + (miktar - 1200000) * 0.14
    elif miktar <= 4800000:
        ucret = 354000 + (miktar - 2400000) * 0.11
    elif miktar <= 9600000:
        ucret = 618000 + (miktar - 4800000) * 0.08
    elif miktar <= 19200000:
        ucret = 1002000 + (miktar - 9600000) * 0.05
    elif miktar <= 38400000:
        ucret = 1482000 + (miktar - 19200000) * 0.03
    else:
        ucret = 2058000 + (miktar - 38400000) * 0.01
        
    # Maktu Sınır Kontrolü (Örn: 45.000 TL) - Dava değerini geçemez kuralı
    maktu_sinir = 45000.0
    if ucret < maktu_sinir:
        ucret = min(maktu_sinir, miktar)
        
    return ucret

# 1. BÖLÜM: Veri Girişi
st.header("📝 1. Dava Bilgileri ve Masraflar")
col1, col2 = st.columns(2)

with col1:
    talep = st.number_input("Dava Değeri / Talep (TL)", min_value=0.0, value=100000.0, step=1000.0)
    kabul = st.number_input("Kabul Edilen Tutar (TL)", min_value=0.0, value=60000.0, step=1000.0)
    pesin_harc = st.number_input("Yatan Peşin + Islah Harcı (TL)", min_value=0.0, value=1707.75, step=10.0)
    
    st.subheader("Taraf Temsili")
    davaci_vekil = st.checkbox("Davacı kendisini vekille temsil ettirdi", value=True)

    if kabul > talep:
        st.error("Kabul edilen tutar, dava değerinden büyük olamaz!")
        kabul = talep

with col2:
    basvuru = st.number_input("Başvurma Harcı (TL)", min_value=0.0, value=732.0, step=10.0)
    d_gider = st.number_input("Davacı Harç Dışı Gideri (TL)", min_value=0.0, value=5000.0, step=100.0)
    dv_gider = st.number_input("Davalı Harç Dışı Gideri (TL)", min_value=0.0, value=0.0, step=100.0)
    
    st.subheader(" ") # Boşluk hizalaması için
    st.write(" ")
    davali_vekil = st.checkbox("Davalı kendisini vekille temsil ettirdi", value=False)

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

# Vekalet Ücretlerinin Hesaplanması
davaci_vekalet = hesapla_vekalet(kabul) if davaci_vekil else 0.0
davali_vekalet = hesapla_vekalet(reddedilen) if davali_vekil else 0.0

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

if davaci_vekil:
    hukum += f"**6-** Davacı yararına AAÜT gereğince hesaplanan {tr_format(davaci_vekalet)} TL vekalet ücretinin DAVALIDAN ALINARAK DAVACIYA VERİLMESİNE,\n\n"

if davali_vekil and reddedilen > 0:
    hukum += f"**7-** Davalı yararına AAÜT gereğince hesaplanan {tr_format(davali_vekalet)} TL vekalet ücretinin DAVACIDAN ALINARAK DAVALIYA VERİLMESİNE,\n\n"

hukum += "**8-** Taraflarca yatırılan gider avansından kullanılmayan kısmın karar kesinleştiğinde HMK m.333 uyarınca yatırana İADESİNE karar verildi."

st.info(hukum)
