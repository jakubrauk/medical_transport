# medical_transport

## Allow non-SSL geolocation
https://stackoverflow.com/questions/39366758/geolocation-without-ssl-connection

## Leaflet awesome-markers
https://github.com/lennardv2/Leaflet.awesome-markers

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


### Kolory markerów EmergencyAlert
- PENDING == red
- IN_PROCESS == green

### Kolory markerów Paramedic
- IN_PROCESS == red
- FREE == blue


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


### TODO
- [x] Responsywna mapa 
- [ ] Sidebar
  - [x] Podstawowy sidebar
  - [ ] Responsywny, zwijany do góry?
  - [ ] Sidebar rozwijany
  - [ ] Zmienne motywy - bg-dark, bg-light
- [x] Django channels - komunikacja na żywo (back-front)
  - [x] Podstawowa komunikacja serwer-front
  - [x] W pełni działająca komunikacja serwer-front
  - [x] websocket automatyczne wznawianie połączenia
- [x] Pokazywanie aktualnej lokalizacji z przeglądarki
- [x] Zapisywanie aktualnej pozycji ratownika
- [x] Zapisywanie ostatniej aktualizacji lokalizacji (watchPositition) - brak możliwości przetestowania lokalnie
- [x] Logowanie, Rejestracja ratowników, dyspozytorów
- [x] Zapisywanie zgłoszeń
- [x] Pokazywanie zgłoszeń
  - [x] Broadcast zgłoszenia
  - [x] aktualizacja zgłoszenia na mapie (broadcast)
  - [x] Pokazywanie i aktualizowanie wszystkich zgłoszeń
- [x] Akceptowanie zgłoszeń
- [x] Finalizowanie zgłoszeń
- [x] Ratownik nie moze przyjac kolejnego zgloszenia jezeli jest zajety
- [x] Zduplikowana lokalizacja ratownika (rozroznienie siebie od innych ratownikow)
- [x] Generowanie i pokazywanie trasy do zgłoszenia
- [x] Pokazywanie izochron
- [x] Pokazywanie zgloszen w izochronie
- [x] Dynamiczne generowanie trasy po zmianie położenia ratownika
- [ ] Pokazywanie przewidywanego czasu dotarcia do zgłoszenia przez ratownika
- [x] Dyspozytor moze bezposrednio dodawac zgloszenia po kliknieciu na mapie
- [x] Dyspozytor moze zobaczyc jakie zgloszenie obsluguje ratownik
- [ ] Dyspozytor moze zobaczyc trase od ratownika do zgloszenia
- [ ] pokazywanie kto i od kiedy jest online
- [ ] usuwanie nieaktywnych ratowników / zgloszen z mapy
  - [ ] celery task do ustawiania ratownikow offline, oraz dezaktywowania zgłoszeń
- [x] Zmiana User z ForeignKey na onetoonefield

### TODO PRACA INZ
- [ ] Opracowanie rozdziałów
  - [ ] Wstęp
    - [ ] Cel pracy
    - [ ] Zakres pracy
  - [ ] Analiza dostępnych rozwiązań
    - [ ] Zoll RescueNet
    - [ ] FirstWatch
    - [ ] PulsePpint
  - [x] Projekt systemu
    - [x] Założenia projektowe
    - [x] Wymagania funkcjonalne
    - [x] Wymagania niefunkcjonalne
    - [x] Diagram przypadków użycia
    - [x] Opis przypadków użycia
    - [x] Diagram relacji między encjami
  - [ ] Wykorzystane technologie
  - [ ] Implementacja
  - [ ] Testy
  - [ ] Podsumowanie


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
