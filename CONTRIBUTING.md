# Contribuir al projecte

Gràcies per considerar contribuir a aquest projecte! Les contribucions són benvingudes i ajuden a millorar l'eina per a tota la comunitat.

## Com contribuir

### Reportar errors

Si trobes un error, si us plau:

1. Verifica que no existeixi ja un issue similar
2. Crea un nou issue amb:
   - Descripció clara del problema
   - Passos per reproduir l'error
   - Comportament esperat vs. comportament actual
   - Informació del sistema (OS, versió Python, etc.)
   - Logs rellevants (sense dades privades!)

### Suggerir millores

Per suggerir noves funcionalitats:

1. Obre un issue amb l'etiqueta "enhancement"
2. Descriu clarament la funcionalitat proposada
3. Explica per què seria útil
4. Proporciona exemples d'ús si és possible

### Contribuir amb codi

1. **Fork** el repositori
2. Crea una **branca** per a la teva funcionalitat:
   ```bash
   git checkout -b feature/nova-funcionalitat
   ```
3. Fes els teus canvis seguint les guies d'estil
4. Afegeix tests si és necessari
5. Assegura't que tots els tests passin
6. Fes **commit** dels teus canvis:
   ```bash
   git commit -m "Afegeix nova funcionalitat"
   ```
7. Fes **push** a la teva branca:
   ```bash
   git push origin feature/nova-funcionalitat
   ```
8. Obre un **Pull Request**

## Guies d'estil

### Codi Python

- Segueix [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilitza noms descriptius per a variables i funcions
- Afegeix docstrings a funcions i classes
- Mantén les línies sota 88 caràcters quan sigui possible
- Utilitza type hints quan sigui apropiat

### Commits

- Utilitza missatges de commit clars i descriptius
- Comença amb un verb en imperatiu ("Afegeix", "Corregeix", "Actualitza")
- Mantén la primera línia sota 50 caràcters
- Afegeix detalls addicionals en línies següents si cal

### Documentació

- Escriu documentació en català
- Utilitza Markdown per a la formatació
- Inclou exemples pràctics
- Actualitza el README si els canvis afecten l'ús

## Configuració de l'entorn de desenvolupament

1. Clona el repositori:
   ```bash
   git clone https://github.com/[usuari]/bluetti-elite200v2-mqtt.git
   cd bluetti-elite200v2-mqtt
   ```

2. Crea un entorn virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instal·la les dependències de desenvolupament:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Si existeix
   ```

4. Configura pre-commit hooks (opcional):
   ```bash
   pre-commit install
   ```

## Tests

Abans d'enviar un PR, assegura't que:

- Tots els tests existents passen
- Has afegit tests per a noves funcionalitats
- El codi té una cobertura adequada

Executa els tests amb:
```bash
python -m pytest
```

## Seguretat

**IMPORTANT**: Mai incloguis dades privades en els teus commits:

- Claus d'encriptació
- Adreces MAC reals
- Credencials MQTT
- Tokens d'autenticació

Utilitza sempre dades d'exemple o placeholders.

## Llicència

En contribuir a aquest projecte, acceptes que les teves contribucions es llicenciïn sota la mateixa llicència MIT del projecte.

## Preguntes

Si tens preguntes sobre com contribuir, pots:

- Obrir un issue amb l'etiqueta "question"
- Contactar els mantenidors del projecte

Gràcies per contribuir! 🎉