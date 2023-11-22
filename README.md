# medical_transport

## Allow non-SSL geolocation
https://stackoverflow.com/questions/39366758/geolocation-without-ssl-connection

w przeglądarce:
```
chrome://flags/#unsafely-treat-insecure-origin-as-secure
```
w CLI:
```bash
google-chrome --args --unsafely-treat-insecure-origin-as-secure="http://whatever.test"
```

uruchomienie serwera:
```bash
python manage.py runserver
```

uruchomienie redis:
```bash
redis-server
```

uruchomienie celery beat:
```bash
celery -A medical_transport beat
```

uruchomienie celery worker:
```bash
celery -A medical_transport worker -B
```




### Opis
Aplikacja webowa do przyjmowania oraz rozdysponowania zgłoszeń alarmowych (konkretna lokalizacja na mapie, priorytet, opcjonalnie finalna destynacja). Na mapie widoczni są zalogowani ratownicy. Dyspozytor widzi wszystkie zgłoszenia oraz wszystkich ratowników. Jeżeli zgłoszenie zostanie przypisane do ratownika, wyznaczana zostaje trasa (openrouteservice).

### Założenia
- Wyświetlanie mapy na żywo ze zgłoszeniami, ratownikami (w zależności od uprawnień - rodzaju użytkownika)
- Akceptowanie zgłoszeń przez ratownika
- Generowanie trasy do zgłoszenia
- Przechowywanie aktualnego położenia ratownika - GPS z przeglądarki

### API do przyjmowania zgłoszeń
- request method: POST
- startPosition - [lat, lng] [float, flaot]
- endPosition (optional) - [lat, lng] [float, flaot]
- priority - int [1-3] 1-normal, 2-medium, 3-high
- additionalInfo - Text


### 6.11.2023 TODO
- [x] Responsywna mapa 
- [ ] Sidebar
  - [x] Podstawowy sidebar
  - [ ] Responsywny, zwijany do góry?
  - [ ] Sidebar rozwijany
  - [ ] Zmienne motywy - bg-dark, bg-light
- [ ] Django channels - komunikacja na żywo (back-front)
  - [x] Podstawowa komunikacja serwer-front
  - [ ] W pełni działająca komunikacja serwer-front
  - [ ] websocket automatyczne wznawianie połączenia
- [x] Pokazywanie aktualnej lokalizacji z przeglądarki
- [x] Zapisywanie aktualnej pozycji ratownika
- [x] Zapisywanie ostatniej aktualizacji lokalizacji (watchPositition) - brak możliwości przetestowania lokalnie
- [x] Logowanie, Rejestracja ratowników, dyspozytorów
- [x] Zapisywanie zgłoszeń
- [x] Pokazywanie zgłoszeń
  - [x] Broadcast zgłoszenia
  - [x] aktualizacja zgłoszenia na mapie (broadcast)
  - [x] Pokazywanie i aktualizowanie wszystkich zgłoszeń
- [ ] Akceptowanie zgłoszeń
- [ ] Generowanie i pokazywanie trasy do zgłoszenia
- [ ] pokazywanie kto i od kiedy jest online
- [ ] usuwanie nieaktywnych ratowników / zgloszen z mapy
  - [ ] celery task do ustawiania offline, oraz dezaktywowania zgłoszeń
- [x] Zmiana User z ForeignKey na onetoonefield


### Konkretny plan działania
 - Rejestracja dyspozytorów (DONE), ratowników (DONE), logowanie (DONE), edycja profilu
 - Przyjmowanie zgłoszeń API - model(DONE), API(DONE), zapis modelu (DONE)
 - pokazywanie live ratowników na mapie (DONE)
 - Pokazywanie zgłoszeń live na mapie (DONE)
 - Pokazywanie zgłoszeń ratownikom w zasięgu, generowanie trasy
 - Rozdysponowanie zgłoszeń między ratownikami, jeżeli nikt nie zaakceptował - wówczas wybór ratownika z listy lub z mapy
 - Uprawnienia dyspozytora
 - Update frontend


### Hierarchia i uprawnienia użytkowników
1. Admin (superuser):
   - Tworzenie kont dyspozytorów
   - Uprawnienia dyspozytora
2. Dyspozytor (user group):
   - Tworzenie kont dla ratowników (Początkowo przypisanych do dyspozytora który go tworzy, można później zmienić)
   - Wyświetlanie wszystkich ratowników na mapie
   - Wyświetlanie wszystkich zgłoszeń na mapie
   - Przydzielanie zgłoszeń do ratownika
3. Ratownik (user group)
   - Pokazywanie ratowników w okolicy (jaka jest ta okolica to do uzgodnienia)
   - Akceptowanie, odrzucanie zgłoszeń alarmowych w okolicy (izochrony)
   - Wyznaczanie trasy do zgłoszenia
   - Potwierdzenie przybycia do celu, kontynuowanie trasy do celu opcjonalnego
   - Zakończenie zgłoszenia alarmowego
   - ? Zapis raportu ze zgłoszenia ?


### Interfejs dla użytkowników (co widzą na mapie)
1. Admin (superuser):
    - Widzi przyciski do tworzenia dyspozytorów
    - Widzi wszystko to co dyspozytor
2. Dyspozytor
    - Widzi wszystkich ratowników na mapie live
    - Widzi wszystkich dyspozytorów live na mapie
    - Widzi wszystkie zgłoszenia na mapie oraz ich status
3. Ratownik
    - Widzi zgłoszenia w swojej okolicy
    - Widzi innych ratowników w swojej okolicy
