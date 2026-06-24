describe("Aplikacja Steganograficzna common components", () => {
  it("powinna poprawnie załadować stronę główną", () => {
    cy.visit("http://localhost:5173");
    cy.get("body").should("exist");
  });
});
