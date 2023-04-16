# web-scrapping-pepper 🌶 (https://www.pepper.pl/)
Final project for Web-scrapping classes on DSBA
To - do:
- [x] bypass "accept cookies" prompt
- [ ] extract bargain info to df
  - [x] extract hottness
  - [x] extract comments
  - [x] extract title
  - [ ] extract price before and after discount
    - [x] extract price values
    - [ ] parse prices to one format
      - [ ] 'ZA DARMO'
      - [ ] prices with '.' as separator (thousands or decimal)
      - [ ] prices with ',' as separator
      - [ ] x % instead of price
      - [ ] 'Allegro Okaze' or similar instead of price value
  - [x] extract username
  - [x] extract link
- [x] scan multiple pages
- [ ] categorize the bargains
- [ ] create notebook with stats of scrapped pages
- [ ] issue with <!-- buffered --> - pages are not scrapped if this comment is present
