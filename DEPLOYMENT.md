# 🚀 Deployment Kılavuzu

Bu kılavuz, 101 Okey AI uygulamasını Netlify ve Render.com üzerinde nasıl deploy edeceğinizi açıklar.

## 📋 Gerekli Dosyalar

### Netlify için (Frontend)
```
public/
├── index.html          # Ana HTML dosyası
├── package.json        # Node.js yapılandırması
└── netlify.toml        # Netlify yapılandırması
```

### Render.com için (Backend)
```
├── app.py              # Flask uygulaması
├── okey_ai.py          # AI motoru
├── requirements.txt    # Python bağımlılıkları
└── render.yaml         # Render yapılandırması
```

## 🌐 Seçenek 1: Tam Stack Deployment (Önerilen)

### Adım 1: Backend'i Render.com'da Deploy Edin

1. **GitHub'a yükleyin**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/username/okeyproje.git
   git push -u origin main
   ```

2. **Render.com'da hesap oluşturun**
   - https://render.com adresine gidin
   - GitHub hesabınızla giriş yapın

3. **Yeni Web Service oluşturun**
   - "New +" → "Web Service"
   - GitHub repository'nizi seçin
   - Aşağıdaki ayarları yapın:
     - **Name**: `okey-ai-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: Free

4. **Deploy edin**
   - "Create Web Service" butonuna tıklayın
   - Deploy işleminin tamamlanmasını bekleyin
   - URL'yi not alın: `https://your-app-name.onrender.com`

### Adım 2: Frontend'i Netlify'da Deploy Edin

1. **Netlify'da hesap oluşturun**
   - https://netlify.com adresine gidin
   - GitHub hesabınızla giriş yapın

2. **Backend URL'yi güncelleyin**
   - `public/index.html` dosyasında:
   ```javascript
   let backendUrl = 'https://your-app-name.onrender.com';
   ```

3. **Deploy edin**
   - "New site from Git" → GitHub repository'nizi seçin
   - Aşağıdaki ayarları yapın:
     - **Base directory**: `public`
     - **Build command**: `npm run build`
     - **Publish directory**: `public`

4. **Custom domain ayarlayın (opsiyonel)**
   - Site settings → Domain management
   - Custom domain ekleyin

## 🌐 Seçenek 2: Sadece Frontend (Statik)

Eğer backend'i ayrı bir serviste çalıştırmak istemiyorsanız:

1. **Backend URL'yi güncelleyin**
   - `public/index.html` dosyasında backend URL'yi değiştirin
   - Veya API proxy kullanın

2. **Netlify'da deploy edin**
   - Sadece `public/` klasörünü yükleyin
   - `netlify.toml` dosyasındaki redirect ayarlarını kullanın

## 🔧 Yapılandırma

### Backend URL Güncelleme

`public/index.html` dosyasında backend URL'yi güncelleyin:

```javascript
// Satır 267'de
let backendUrl = 'https://your-backend-url.onrender.com';
```

### CORS Ayarları

Backend'de CORS zaten yapılandırılmış. Eğer sorun yaşarsanız:

```python
# app.py
from flask_cors import CORS
app = Flask(__name__)
CORS(app, origins=['https://your-netlify-site.netlify.app'])
```

### Environment Variables

Render.com'da environment variables ekleyebilirsiniz:

```bash
FLASK_ENV=production
PORT=10000
```

## 🧪 Test Etme

### Backend Test
```bash
curl -X POST https://your-backend-url.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"tiles":[],"indicator":{},"discarded_tiles":[]}'
```

### Frontend Test
- Netlify URL'nizi ziyaret edin
- Taş seçin ve analiz yapın
- Console'da hata olup olmadığını kontrol edin

## 🚨 Sorun Giderme

### Backend Sorunları

1. **Import hatası**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port sorunu**
   ```python
   # app.py
   port = int(os.environ.get('PORT', 5000))
   ```

3. **CORS hatası**
   ```python
   CORS(app, origins=['*'])  # Geçici çözüm
   ```

### Frontend Sorunları

1. **API çağrısı hatası**
   - Backend URL'nin doğru olduğunu kontrol edin
   - Network tab'ında hataları inceleyin

2. **Build hatası**
   - `package.json` dosyasının doğru olduğunu kontrol edin
   - Netlify build loglarını inceleyin

## 📊 Monitoring

### Render.com
- Dashboard'da logları görüntüleyin
- Performance metrics'i takip edin

### Netlify
- Site analytics'i kontrol edin
- Function logs'u inceleyin

## 🔄 Güncelleme

### Backend Güncelleme
```bash
git add .
git commit -m "Update backend"
git push origin main
# Render otomatik deploy edecek
```

### Frontend Güncelleme
```bash
git add .
git commit -m "Update frontend"
git push origin main
# Netlify otomatik deploy edecek
```

## 💰 Maliyet

### Ücretsiz Planlar
- **Render.com**: 750 saat/ay (yaklaşık 31 gün)
- **Netlify**: 100GB bandwidth/ay

### Ücretli Planlar
- **Render.com**: $7/ay (sınırsız)
- **Netlify**: $19/ay (Pro plan)

## 🎯 Sonuç

Başarılı deployment sonrası:
- Frontend: `https://your-site.netlify.app`
- Backend: `https://your-app.onrender.com`
- API: `https://your-app.onrender.com/api/*`

Her iki servis de otomatik olarak güncellenecek ve 7/24 çalışacaktır. 