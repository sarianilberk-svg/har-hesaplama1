import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Harç ve Yargılama Gideri Hesaplama", layout="wide")
st.title("⚖️ Harç ve Yargılama Gideri Hesaplama")
st.markdown("Bu uygulama, girdiğiniz verilere göre yargılama giderlerini, harçları oranlar ve otomatik hüküm fıkrası oluşturur.")

# 1. BÖLÜM: GİRDİLER (Kullanıcının veri gireceği yerler)
st.header("📝 1. Dava Bilgileri (Girdiler)")
col1, col2 = st.columns(2)

with col1:
    talep = st.number_input("Talep Edilen Miktar (TL)", min_value=0.0, value=1000000.0, step=1000.0)
    islah = st.number_input("Islah Edilen Miktar (TL) (Varsa)", min_value=0.0, value=0.0, step=1000.0)
    toplam_deger = talep + islah
    st.info(f"**Toplam Dava Değeri:** {toplam_deger:,.2f} TL")
    
    kabul_edilen = st.number_input("Davada Kabul Edilen Miktar (TL)", min_value=0.0, max_value=toplam_deger, value=toplam_deger, step=1000.0)
    reddedilen = toplam_deger - kabul_edilen
    st.warning(f"**Reddedilen Miktar:** {reddedilen:,.2f} TL")

with col2:
    davaci_gider = st.number_input("Davacının Yaptığı Posta/Tebligat Gideri (TL)", min_value=0.0, value=1896.40)
    davaci_pesin_harc = st.number_input("Davacının Yatırdığı Peşin/Tamamlama Harcı Toplamı (TL)", min_value=0.0, value=17077.50)
    davali_gider = st.number_input("Davalının Yaptığı Yargılama Gideri (TL)", min_value=0.0, value=1625.32)

# 2. BÖLÜM: HESAPLAMALAR (Arka planda çalışan matematik)
if toplam_deger > 0:
    kabul_orani = kabul_edilen / toplam_deger
    ret_orani = reddedilen / toplam_deger
else:
    kabul_orani = 0; ret_orani = 0

davaci_karsilanacak = davaci_gider * kabul_orani
davali_karsilanacak = davali_gider * ret_orani
alinmasi_gereken_harc = kabul_edilen * (68.31 / 1000) # Nispi harç oranı (Binde 68.31)
bakiye_harc = alinmasi_gereken_harc - davaci_pesin_harc

st.divider()

# 3. BÖLÜM: SONUÇLAR VE HÜKÜM FIKRASI
st.header("⚖️ 2. Hesaplama Sonuçları ve Hüküm Fıkrası")

if kabul_edilen == toplam_deger:
    st.success("📌 DURUM: DAVANIN TAMAMEN KABULÜ")
    hukum = f"""
    **1-** Davanın KABULÜNE,
    **2-** Dava nedeniyle alınması gereken {alinmasi_gereken_harc:,.2f} TL karar ve ilam harcından, davacı tarafça ikmal edilen {davaci_pesin_harc:,.2f} TL harcın mahsubu ile bakiye {bakiye_harc:,.2f} TL harcın davalıdan alınarak Hazineye gelir kaydına,
    **3-** Davacının yaptığı {davaci_gider:,.2f} TL yargılama giderinin davalıdan alınarak davacıya verilmesine...
    """
    st.markdown(hukum)

elif reddedilen == toplam_deger:
    st.error("📌 DURUM: DAVANIN TAMAMEN REDDİ")
    hukum = f"""
    **1-** Davanın REDDİNE,
    **2-** Alınması gereken maktu karar harcının, peşin alınan {davaci_pesin_harc:,.2f} TL harçtan mahsubu ile kalan kısmın talep halinde iadesine,
    **3-** Davalı tarafın yaptığı {davali_gider:,.2f} TL yargılama giderinin davacıdan alınarak davalıya verilmesine...
    """
    st.markdown(hukum)

else:
    st.info("📌 DURUM: DAVANIN KISMEN KABULÜ, KISMEN REDDİ")
    hukum = f"""
    **1-** Davanın KISMEN KABULÜNE, KISMEN REDDİNE,
    **2-** Dava nedeniyle alınması gereken {alinmasi_gereken_harc:,.2f} TL karar ve ilam harcından, davacı tarafça ikmal edilen {davaci_pesin_harc:,.2f} TL harcın mahsubu ile bakiye {bakiye_harc:,.2f} TL harcın davalıdan alınarak Hazineye gelir kaydına,
    **3-** Davacının yaptığı toplam {davaci_gider:,.2f} TL yargılama giderinin kabul oranına göre hesaplanan **{davaci_karsilanacak:,.2f} TL**'sinin davalıdan alınarak davacıya verilmesine,
    **4-** Davalının yaptığı toplam {davali_gider:,.2f} TL yargılama giderinin ret oranına göre hesaplanan **{davali_karsilanacak:,.2f} TL**'sinin davacıdan alınarak davalıya verilmesine...
    """
    st.markdown(hukum)
