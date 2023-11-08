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

### Opis
Aplikacja webowa do przyjmowania oraz rozdysponowania zgłoszeń alarmowych (konkretna lokalizacja na mapie, priorytet, opcjonalnie finalna destynacja). Na mapie widoczni są zalogowani ratownicy. Dyspozytor widzi wszystkie zgłoszenia oraz wszystkich ratowników. Jeżeli zgłoszenie zostanie przypisane do ratownika, wyznaczana zostaje trasa (openrouteservice).

### Założenia
- Wyświetlanie mapy na żywo ze zgłoszeniami, ratownikami (w zależności od uprawnień - rodzaju użytkownika)
- Akceptowanie zgłoszeń przez ratownika
- Generowanie trasy do zgłoszenia
- Przechowywanie aktualnego położenia ratownika - GPS z przeglądarki


### 6.11.2023 TODO
- [x] Responsywna mapa 
- [ ] Sidebar
  - [x] Podstawowy sidebar
  - [ ] Responsywny, zwijany do góry?
  - [ ] Sidebar rozwijany
  - [ ] Zmienne motywy - bg-dark, bg-light
- [ ] Django channels - komunikacja na żywo (back-front)
  - [x] Podstawowa komunikacja serwer-front
  - [ ] Osobne channels dla dyspozytorów i ratowników
  - [ ] W pełni działająca komunikacja serwer-front
- [x] Pokazywanie aktualnej lokalizacji z przeglądarki
- [ ] Logowanie, Rejestracja ratowników, dyspozytorów
- [ ] Zapisywanie aktualnej pozycji ratownika
- [ ] Zapisywanie zgłoszeń
- [ ] Pokazywanie zgłoszeń
- [ ] Akceptowanie zgłoszeń
- [ ] Generowanie i pokazywanie trasy do zgłoszenia
