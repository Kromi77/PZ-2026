describe("Aplikacja Steganograficzna encode view", () => {
  it("powinna zablokować kodowanie bez wybranego pliku", () => {
    cy.visit("http://localhost:5173");

    cy.get("textarea").type("To jest testowa wiadomość od Cypressa");

    cy.get("button").contains("Zakoduj").click();

    cy.contains("Wybierz plik").should("be.visible");
  });

  it("powinna załadować plik bmp, wpisać tekst i rozpocząć kodowanie", () => {
    cy.visit("http://localhost:5173");

    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/sample_640x480.bmp",
      { force: true },
    );

    cy.get("textarea").type("To jest sekretna wiadomość dla Cypressa");
    cy.get("button").contains("Zakoduj").click();
    cy.get("body").should("not.contain", "Wybierz plik");
  });
});
