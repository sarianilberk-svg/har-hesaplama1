import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Harç ve Yargılama Gideri Hesaplama", layout="wide")
st.title("⚖️ Kapsamlı Harç ve Hüküm Fıkrası Hesaplama")
st.markdown("Bu uygulama Excel'deki 'Nispi Harçlar, Kabul, Kısmen Kabul ve Ret' sayfalarındaki tüm mantığı birebir barındırır.")

# Türk Lirası formatı için yardımcı fonksiyon (1.000.000,00 TL formatı için)
def format_tr(miktar):
    return f"{miktar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# 1. BÖLÜM: DAVA BİLGİLERİ (GİRDİLER)
st.header("📝 1. Dava Değerleri ve Giderler")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Talepler")
    harc_turu = st.selectbox("Harç Türü Oranı", ["Genel Nispi (68,31)", "Sulh Hukuk (13,65)", "Tahliye Davası (11,68)", "İcra Takip (4,55)"])
    
    # Harç oranını belirleme
    if harc_turu == "Genel Nispi (68,31)": oran = 68.31 / 1000
    elif harc_turu == "Sulh Hukuk (13,65)": oran = 13.65 / 1000
    elif harc_turu == "Tahliye Davası (11,68)": oran = 11.68 / 1000
    else: oran = 4.55 / 1000

    talep = st.number_input("Talep Edilen Miktar (TL)", min_value=0.0, value=1000000.0, step=1000.0)
    islah = st.number_input("Islah Edilen Miktar (TL)", min_value=0.0, value=13000000.0, step=1000.0)
    
    toplam_deger = talep + islah
    st.info(f"**Toplam Dava Değeri:** {format_tr(toplam_deger)} TL")
    
    kabul_edilen = st.number_input("Kabul Edilen Miktar (TL)", min_value=0.0, max_value=toplam_deger, value=11000000.0, step=1000.0)
    reddedilen = toplam_deger - kabul_edilen
    st.warning(f"**Reddedilen Miktar:** {format_tr(reddedilen)} TL")

with col2:
    st.subheader("Harç ve Masraflar")
    basvuru_harci = st.number_input("Maktu Başvurma Harcı (TL)", value=615.40)
    maktu_karar_harci = st.number_input("Maktu Karar Harcı (TL) (Ret Durumu İçin)", value=732.00)
    
    # Excel mantığı: Peşin harç talep üzerinden 1/4 alınır. Islah harcı da ıslah üzerinden 1/4 alınır.
    hesaplanan_pesin = (talep * oran) / 4
    hesaplanan_islah = (islah * oran) / 4
    
    pesin_harc = st.number_input("Yatırılan Peşin Harç (TL)", value=hesaplanan_pesin)
    islah_harci = st.number_input("Yatırılan Tamamlama/Islah Harcı (TL)", value=hesaplanan_islah)
    toplam_yatan_harc = pesin_harc + islah_harci
    
    davaci_gider = st.number_input("Davacının Posta/Tebligat Gideri (TL)", value=1896.40)
    davali_gider = st.number_input("Davalının Posta/Tebligat Gideri (TL)", value=1625.32)

with col3:
    st.subheader("Ücretler")
    davaci_vekalet = st.number_input("Davacı Vekalet Ücreti (TL)", value=1072000.00)
    davali_vekalet = st.number_input("Davalı Vekalet Ücreti (TL)", value=420000.00)
    arabuluculuk_ucreti = st.number_input("Arabuluculuk Ücreti (TL)", value=2200.00)
    arabuluculuk_kimden = st.selectbox("Arabuluculuk Kime Yüklenecek?", ["Davacıdan alınarak Hazineye", "Davalıdan alınarak Hazineye", "Haklılık Oranına Göre Paylaştır"])

# 2. BÖLÜM: HESAPLAMALAR (EXCEL'İN ARKA PLANI)
if toplam_deger > 0:
    kabul_orani = kabul_edilen / toplam_deger
    ret_orani = reddedilen / toplam_deger
else:
    kabul_orani = 0; ret_orani = 0

davaci_karsilanacak = davaci_gider * kabul_orani
davali_karsilanacak = davali_gider * ret_orani

# Nispi Harç Hesabı (Kabul Edilen Miktar Üzerinden)
alinmasi_gereken_nispi = kabul_edilen * oran
bakiye_nispi_harc = alinmasi_gereken_nispi - toplam_yatan_harc
iade_edilecek_harc = 0

if bakiye_nispi_harc < 0:
    iade_edilecek_harc = abs(bakiye_nispi_harc)
    bakiye_nispi_harc = 0

st.divider()

# 3. BÖLÜM: HÜKÜM FIKRASI
st.header("📜 Otomatik Hüküm Fıkrası")

# Arabuluculuk Metni
ara_metin = ""
if arabuluculuk_ucreti > 0:
    if arabuluculuk_kimden == "Davacıdan alınarak Hazineye":
        ara_metin = f"Dava açılmadan önce taraflar arasında arabuluculuk görüşmeleri yapılmış olmakla Adalet Bakanlığı bütçesinden sarf edilen {format_tr(arabuluculuk_ucreti)} TL arabuluculuk ücretinin davacıdan alınarak Hazineye gelir kaydına,"
    elif arabuluculuk_kimden == "Davalıdan alınarak Hazineye":
        ara_metin = f"Dava açılmadan önce taraflar arasında arabuluculuk görüşmeleri yapılmış olmakla Adalet Bakanlığı bütçesinden sarf edilen {format_tr(arabuluculuk_ucreti)} TL arabuluculuk ücretinin davalıdan alınarak Hazineye gelir kaydına,"
    else:
        davaci_ara = arabuluculuk_ucreti * ret_orani # Reddedilen kısım davacı üstünde kalır
        davali_ara = arabuluculuk_ucreti * kabul_orani
        ara_metin = f"Dava açılmadan önce taraflar arasında arabuluculuk görüşmeleri yapılmış olmakla Adalet Bakanlığı bütçesinden sarf edilen {format_tr(arabuluculuk_ucreti)} TL arabuluculuk ücretinin haklılık oranına göre {format_tr(davali_ara)} TL'sinin davalıdan, {format_tr(davaci_ara)} TL'sinin davacıdan alınarak Hazineye gelir kaydına,"

ortak_son = f"""
**8-** Kararın talep halinde ve masrafı karşılandığında taraflara tebliğine,
**9-** Kalan gider avansının karar kesinleştiğinde yatıran tarafa iadesine,

*Dair, kararın tebliğinden itibaren iki hafta içerisinde mahkememize sunulacak, yahut mahkememize gönderilmek üzere bir başka mahkemeye ibraz edilecek bir dilekçeyle başvuru yapılmak suretiyle, Bölge Adliye Mahkemeleri ilgili Hukuk Dairesi nezdinde istinaf kanun yolu açık olmak üzere karar verildi.*
"""

if toplam_deger == 0:
    st.warning("Hesaplama için lütfen değer giriniz.")

elif kabul_edilen == toplam_deger: # TAM KABUL
    st.success("📌 DURUM: KABUL")
    hukum = f"""
**1-** Davanın KABULÜNE,
**2-** Dava nedeniyle alınması gereken {format_tr(alinmasi_gereken_nispi)} TL karar ve ilam harcından davacı tarafça ikmal edilen {format_tr(pesin_harc)} TL peşin harç ve {format_tr(islah_harci)} TL tamamlama harcının mahsubu ile bakiye {format_tr(bakiye_nispi_harc)} TL harcın davalıdan/davalılardan müştereken ve müteselsilen tahsili ile Hazineye gelir kaydına,
**3-** Davacının ikmal etmiş olduğu {format_tr(pesin_harc)} TL peşin harç ile {format_tr(basvuru_harci)} TL başvuru harcı ve {format_tr(islah_harci)} TL tamamlama harcının toplamı olan {format_tr(basvuru_harci+toplam_yatan_harc)} TL'nin davalıdan/davalılardan alınarak davacıya verilmesine,
**4-** Davacının yaptığı yargılama giderleri olan tebligat ve müzekkere posta giderlerinden oluşan toplam {format_tr(davaci_gider)} TL'nin davalıdan alınarak davacıya verilmesine,
**5-** Davalının yaptığı yargılama giderleri olan toplam {format_tr(davali_gider)} TL'nin davalı üzerinde bırakılmasına,
**6-** Davacı davada kendisini vekil ile temsil ettirdiğinden hüküm tarihinde geçerli Avukatlık Asgari Ücret Tarifesine göre hesaplanan {format_tr(davaci_vekalet)} TL vekalet ücretinin davalıdan alınarak davacıya verilmesine,
**7-** {ara_metin}
{ortak_son}
"""
    st.markdown(hukum)

elif reddedilen == toplam_deger: # TAM RET
    st.error("📌 DURUM: RET")
    hukum = f"""
**1-** Davanın REDDİNE,
**2-** Dava nedeniyle alınması gereken {format_tr(maktu_karar_harci)} TL maktu karar ve ilam harcının, davacı tarafça ikmal edilen {format_tr(pesin_harc)} TL peşin harç ve {format_tr(islah_harci)} TL ıslah harcından mahsubu ile fazla alınan {format_tr(toplam_yatan_harc - maktu_karar_harci)} TL harcın karar kesinleştiğinde ve talep halinde davacıya iadesine,
**3-** Davacı tarafın yaptığı tebligat ve müzekkere posta giderlerinden oluşan toplam {format_tr(davaci_gider)} TL'nin davacı taraf üzerinde bırakılmasına,
**4-** Davalı tarafın yaptığı tebligat ve müzekkere posta giderlerinden oluşan toplam {format_tr(davali_gider)} TL'nin davacıdan alınarak davalıya verilmesine,
**5-** Davalı davada kendisini vekil ile temsil ettirdiğinden hüküm tarihinde geçerli Avukatlık Asgari Ücret Tarifesine göre hesaplanan {format_tr(davali_vekalet)} TL vekalet ücretinin davacıdan alınarak davalıya verilmesine,
**6-** {ara_metin}
{ortak_son}
"""
    st.markdown(hukum)

else: # KISMEN KABUL KISMEN RET
    st.info("📌 DURUM: KISMEN KABUL")
    hukum = f"""
**1-** Davanın KISMEN KABULÜNE, KISMEN REDDİNE,
**2-** Dava nedeniyle alınması gereken {format_tr(alinmasi_gereken_nispi)} TL karar ve ilam harcından davacı tarafça ikmal edilen {format_tr(pesin_harc)} TL peşin harç ve {format_tr(islah_harci)} TL tamamlama harcının mahsubu ile bakiye {format_tr(bakiye_nispi_harc)} TL harcın davalıdan tahsili ile Hazineye gelir kaydına,
**3-** Davacının ikmal etmiş olduğu {format_tr(pesin_harc)} TL peşin harç ile {format_tr(basvuru_harci)} TL başvuru harcı ve {format_tr(islah_harci)} TL tamamlama harcının toplamı olan {format_tr(basvuru_harci+toplam_yatan_harc)} TL'nin davalıdan alınarak davacı tarafa verilmesine,
**4-** Davacının yaptığı {format_tr(davaci_gider)} TL yargılama giderinin kabul oranına (%{kabul_orani*100:.2f}) tekabül eden {format_tr(davaci_karsilanacak)} TL'sinin davalıdan alınarak davacıya verilmesine, kalan kısmın davacı üzerinde bırakılmasına,
**5-** Davalının yaptığı {format_tr(davali_gider)} TL yargılama giderinin ret oranına (%{ret_orani*100:.2f}) tekabül eden {format_tr(davali_karsilanacak)} TL'sinin davacıdan alınarak davalıya verilmesine, kalan kısmın davalı üzerinde bırakılmasına,
**6-** Davacı davada kendisini vekil ile temsil ettirdiğinden kabul edilen miktar üzerinden hesaplanan {format_tr(davaci_vekalet)} TL vekalet ücretinin davalıdan alınarak davacıya verilmesine,
**7-** Davalı davada kendisini vekil ile temsil ettirdiğinden reddedilen miktar üzerinden hesaplanan {format_tr(davali_vekalet)} TL vekalet ücretinin davacıdan alınarak davalıya verilmesine,
**8-** {ara_metin}
{ortak_son}
"""
    st.markdown(hukum)

st.markdown("---")
st.caption("Not: Bu uygulama otomatik hesaplama yapar. Hüküm fıkrasını kopyaladıktan sonra lütfen mahkemenize özgü detayları (faiz başlangıç tarihi, müştereken ve müteselsilen ibareleri vb.) son bir kez kontrol ediniz.")
