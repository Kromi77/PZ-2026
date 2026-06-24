const BASE_URL = "http://localhost:5173";

describe("Aplikacja Steganograficzna encode view", () => {
  it("powinna zablokować kodowanie bez wybranego pliku", () => {
    cy.visit(BASE_URL);

    cy.get("textarea").type("To jest testowa wiadomość od Cypressa");

    cy.get("button").contains("Zakoduj").click();

    cy.contains("Wybierz plik").should("be.visible");
  });

  it("powinna zablokować kodowanie bez wybranego wpisanego klucza", () => {
    cy.visit(BASE_URL);

    cy.get("textarea").type("To jest testowa wiadomość od Cypressa");
    cy.get('input[placeholder="Wpisz klucz"]').first().clear();

    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/sample_640x480.bmp",
      { force: true },
    );
    cy.get("button").contains("Zakoduj").click();

    cy.contains("Podaj klucz").should("be.visible");
  });

  it("powinna załadować plik bmp, wpisać tekst i rozpocząć kodowanie", () => {
    cy.visit(BASE_URL);

    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/sample_640x480.bmp",
      { force: true },
    );

    cy.get("textarea").type("To jest sekretna wiadomość dla Cypressa");
    cy.get("button").contains("Zakoduj").click();
    cy.get("body").should("not.contain", "Wybierz plik");
  });

  it("powinna załadować plik audio (WAV), zmienić opcje i ukryć w nim wiadomość", () => {
    cy.visit(BASE_URL);

    // 1. Wpisanie wiadomości w pole tekstowe
    cy.get("textarea").type("Testujemy kodowanie w fali dźwiękowej!");

    // 2. Wybór z listy rozwijanej (Selektor na "Szyfr kolumnowy")
    cy.get("select").first().select("Szyfr Cezara");

    cy.get('input[placeholder="Wpisz klucz"]').first().clear().type("13");

    cy.get('input[type="file"]').selectFile("cypress/fixtures/sample-3.wav", {
      force: true,
    });

    cy.contains("Głębia LSB dla WAV").should("be.visible");

    cy.get('input[type="range"]')
      .filter(":visible")
      .first()
      .then(($slider) => {
        // Wyciągamy czysty element HTML z Cypressa
        const el = $slider[0];

        // Kradniemy natywną funkcję przeglądarki do ustawiania wartości
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
          window.HTMLInputElement.prototype,
          "value",
        ).set;

        // Ustawiamy wartość na 2 (Z pominięciem zabezpieczeń Reacta)
        nativeInputValueSetter.call(el, 2);

        // Odpalamy flarę ratunkową - wysyłamy bąbelkujące zdarzenia,
        // które zmuszają Reacta do przerysowania widoku!
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
      });

    cy.contains("button", "Zakoduj i ukryj wiadomość").click();

    cy.get("body").should("not.contain", "Wybierz plik");
    cy.get("#root input.rounded-full").click();
  });

  it("powinna załadować obraz (BMP), zmienić 3 suwaki RGB i ukryć wiadomość", () => {
    cy.visit("http://localhost:5173");

    // 1. Wpisanie wiadomości
    cy.get("textarea").type(
      "Testujemy zaawansowane kodowanie w pikselach BMP!",
    );
    cy.get("select").first().select("Szyfr XOR");
    cy.get('input[placeholder="Wpisz klucz"]')
      .first()
      .clear()
      .type("tajnySECRET");
    // 2. Wgranie obrazka BMP
    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/sample_640x480.bmp",
      {
        force: true,
      },
    );

    // 3. Upewniamy się, że React wyrenderował sekcję dla BMP
    cy.contains("Kanały BMP").should("be.visible");

    // --- NASZA SUPER-BROŃ NA SUWAKI REACTA ---
    // Tworzymy małą funkcję wewnątrz testu, żeby nie powtarzać kodu 3 razy
    const setReactSliderValue = ($slider, value) => {
      const el = $slider[0];
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        "value",
      ).set;

      nativeSetter.call(el, value);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    };

    // 4. Ustawiamy suwak R (Indeks 0) na wartość 2
    cy.get('input[type="range"]')
      .filter(":visible")
      .eq(0)
      .then(($slider) => setReactSliderValue($slider, 2));

    // 5. Ustawiamy suwak G (Indeks 1) na wartość 3
    cy.get('input[type="range"]')
      .filter(":visible")
      .eq(1)
      .then(($slider) => setReactSliderValue($slider, 3));

    // 6. Ustawiamy suwak B (Indeks 2) na wartość 4
    cy.get('input[type="range"]')
      .filter(":visible")
      .eq(2)
      .then(($slider) => setReactSliderValue($slider, 4));

    // 7. Zmiana trybu rozmieszczenia na "Równomiernie"
    cy.contains("Równomierne").click();

    // 8. Odpalenie kodowania
    cy.contains("button", "Zakoduj i ukryj wiadomość").click();

    // 9. Weryfikacja (upewniamy się, że proces ruszył i nie wywalił błędu braku pliku)
    cy.get("body").should("not.contain", "Wybierz plik");
  });
});
