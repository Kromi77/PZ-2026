const BASE_URL = "http://localhost:5173";

describe("Aplikacja Steganograficzna common components", () => {
  beforeEach(() => {
    cy.visit(BASE_URL);
  });

  it("powinna poprawnie załadować stronę główną", () => {
    cy.get("body").should("exist");
  });

  it("powinna wyświetlać główny layout aplikacji", () => {
    cy.get("header").should("be.visible");
    cy.get("main").should("be.visible");
  });

  it("powinna wyświetlać nagłówek strony", () => {
    cy.get("header h1")
      .should("be.visible")
      .invoke("text")
      .should("match", /\S+/);
  });

  it("powinna wyświetlać informację o obsługiwanych trybach", () => {
    cy.get("header").within(() => {
      cy.contains("Tryb:").should("be.visible");
      cy.contains("BMP / WAV").should("be.visible");
    });
  });

  it("powinna wyświetlać podtytuł, jeżeli został przekazany do Header", () => {
    cy.get("header").then(($header) => {
      const subtitle = $header.find("p");

      if (subtitle.length > 0) {
        cy.wrap(subtitle)
          .should("be.visible")
          .invoke("text")
          .should("match", /\S+/);
      }
    });
  });

  it("powinna wyświetlać badge, jeżeli został przekazany do Header", () => {
    cy.get("header").then(($header) => {
      const badge = $header.find("span").filter((_, element) => {
        return element.className.includes("uppercase");
      });

      if (badge.length > 0) {
        cy.wrap(badge)
          .should("be.visible")
          .invoke("text")
          .should("match", /\S+/);
      }
    });
  });

  it("powinna wyświetlać główną sekcję treści", () => {
    cy.get("main")
      .should("be.visible")
      .and("have.class", "flex")
      .and("have.class", "flex-col");
  });

  it("powinna wyświetlać nawigację z dwoma zakładkami", () => {
    cy.get("button[aria-pressed]").should("have.length", 2);

    cy.get("button[aria-pressed]")
      .eq(0)
      .should("be.visible")
      .and("not.be.empty");

    cy.get("button[aria-pressed]")
      .eq(1)
      .should("be.visible")
      .and("not.be.empty");
  });

  it("pierwsza zakładka powinna być aktywna po wejściu na stronę", () => {
    cy.get("button[aria-pressed]")
      .eq(0)
      .should("have.attr", "aria-pressed", "true");

    cy.get("button[aria-pressed]")
      .eq(1)
      .should("have.attr", "aria-pressed", "false");
  });

  it("powinna zmieniać aktywną zakładkę po kliknięciu", () => {
    cy.get("button[aria-pressed]").eq(1).click();

    cy.get("button[aria-pressed]")
      .eq(0)
      .should("have.attr", "aria-pressed", "false");

    cy.get("button[aria-pressed]")
      .eq(1)
      .should("have.attr", "aria-pressed", "true");
  });

  it("powinna pozwalać wrócić do pierwszej zakładki", () => {
    cy.get("button[aria-pressed]").eq(1).click();

    cy.get("button[aria-pressed]")
      .eq(1)
      .should("have.attr", "aria-pressed", "true");

    cy.get("button[aria-pressed]").eq(0).click();

    cy.get("button[aria-pressed]")
      .eq(0)
      .should("have.attr", "aria-pressed", "true");

    cy.get("button[aria-pressed]")
      .eq(1)
      .should("have.attr", "aria-pressed", "false");
  });

  it("przyciski zakładek powinny mieć typ button", () => {
    cy.get("button[aria-pressed]").each(($button) => {
      cy.wrap($button).should("have.attr", "type", "button");
    });
  });
});
