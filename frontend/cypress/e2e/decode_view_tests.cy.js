const BASE_URL = "http://localhost:5173";

function goToDecodeView() {
  cy.visit(BASE_URL);

  cy.get("button[aria-pressed]").then(($tabs) => {
    const decodeTab = [...$tabs].find((tab) =>
      /decode|dekod|odkod/i.test(tab.innerText),
    );

    if (decodeTab) {
      cy.wrap(decodeTab).click();
    } else {
      cy.wrap($tabs.eq(1)).click();
    }
  });
}

function uploadBmpFile() {
  cy.get('input[type="file"]').selectFile(
    "cypress/fixtures/sample_640x480.bmp",
    { force: true },
  );
}

function uploadWavFile() {
  cy.get('input[type="file"]').selectFile("cypress/fixtures/sample-3.wav", {
    force: true,
  });
}

describe("Aplikacja Steganograficzna decode view", () => {
  beforeEach(() => {
    goToDecodeView();
  });

  it("powinna poprawnie wyświetlać widok dekodowania", () => {
    cy.contains("Raport dekodowania").should("be.visible");

    cy.contains("Szyfr użyty przy kodowaniu").should("be.visible");
    cy.contains("Klucz użyty przy kodowaniu").should("be.visible");
    cy.contains("Tryb rozmieszczenia użyty przy kodowaniu").should(
      "be.visible",
    );

    cy.get("main").should("be.visible");
  });

  it("powinna wyświetlać pole wyboru pliku zakodowanego", () => {
    cy.get('input[type="file"]')
      .should("exist")
      .and("have.attr", "accept", ".bmp,.wav");

    cy.contains("Kliknij, aby wybrać plik").should("be.visible");
  });

  it("powinna pozwalać wczytać plik BMP z fixtures", () => {
    uploadBmpFile();

    cy.contains("sample_640x480.bmp").should("be.visible");
  });

  it("powinna pozwalać wczytać plik WAV z fixtures", () => {
    uploadWavFile();

    cy.contains("sample-3.wav").should("be.visible");
  });

  it("powinna wyświetlać i obsługiwać pole wyboru szyfru", () => {
    cy.contains("label", "Szyfr użyty przy kodowaniu")
      .find("select")
      .should("be.visible")
      .find("option")
      .should("have.length.greaterThan", 0);

    cy.contains("label", "Szyfr użyty przy kodowaniu")
      .find("select")
      .then(($select) => {
        const firstValue = $select.find("option").eq(0).val();

        cy.wrap($select).select(firstValue);
        cy.wrap($select).should("have.value", firstValue);
      });
  });

  it("powinna pozwalać wyczyścić input klucza i wpisać liczbę", () => {
    cy.contains("label", "Klucz użyty przy kodowaniu")
      .find('input[type="text"]')
      .should("be.visible")
      .clear()
      .should("have.value", "")
      .type("123")
      .should("have.value", "123");
  });

  it("powinna wyświetlać suwaki parametrów dekodowania", () => {
    cy.get('input[type="range"]').should("exist");

    cy.get('input[type="range"]').each(($slider) => {
      cy.wrap($slider)
        .should("have.attr", "min", "0")
        .and("have.attr", "max", "8")
        .and("have.attr", "step", "1");
    });
  });

  it("powinna pozwalać zmienić wartość pierwszego suwaka", () => {
    cy.get('input[type="range"]').first().as("firstSlider");

    cy.get("@firstSlider")
      .invoke("val", "4")
      .trigger("input", { force: true })
      .trigger("change", { force: true });

    cy.get("@firstSlider").should("have.value", "4");
  });

  it("powinna wyświetlać tryby rozmieszczenia wiadomości", () => {
    cy.contains("Tryb rozmieszczenia użyty przy kodowaniu")
      .should("be.visible")
      .parent()
      .within(() => {
        cy.get('input[type="radio"][name="decode-deployment"]').should(
          "have.length",
          2,
        );
      });
  });

  it("powinna pozwalać zmienić tryb rozmieszczenia", () => {
    cy.get('input[type="radio"][name="decode-deployment"]')
      .eq(1)
      .check({ force: true })
      .should("be.checked");

    cy.get('input[type="radio"][name="decode-deployment"]')
      .eq(0)
      .check({ force: true })
      .should("be.checked");
  });

  it("powinna wyświetlać przycisk dekodowania", () => {
    cy.contains("button:not([aria-pressed])", /Odczyt/i)
      .should("be.visible")
      .and("have.attr", "type", "button");
  });

  it("na początku nie powinna wyświetlać raportu z wynikiem", () => {
    cy.contains("Wiadomość wykryta").should("not.exist");
    cy.contains("Zaszyfrowany tekst wyciągnięty z pliku").should("not.exist");
  });

  it("po wczytaniu pliku BMP powinna wyświetlić wybrany plik", () => {
    uploadBmpFile();

    cy.contains("sample_640x480.bmp").should("be.visible");
  });

  it("po wczytaniu pliku WAV powinna wyświetlić wybrany plik", () => {
    uploadWavFile();

    cy.contains("sample-3.wav").should("be.visible");
  });
});
