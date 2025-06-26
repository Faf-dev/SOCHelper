/**
 * @jest-environment jsdom
 */
import "../js/deleteHandler.js";

describe("Suppression via bouton .btn_delete", () => {
  let tbody, btn, tr;

  beforeEach(() => {
    // Simule le DOM du tableau avec un bouton de suppression
    document.body.innerHTML = `
      <section class="log-table">
        <table>
          <tbody>
            <tr>
              <td>2025-06-25</td>
              <td>12:00</td>
              <td>1.2.3.4</td>
              <td>SQL_INJECTION</td>
              <td>/test</td>
              <td><button class="btn_delete" data-id="42" data-type="event"></button></td>
            </tr>
          </tbody>
        </table>
      </section>
    `;
    tbody = document.querySelector(".log-table tbody");
    btn = document.querySelector(".btn_delete");
    tr = btn.closest("tr");
    // Mock le token
    sessionStorage.setItem("token", "fake-token");
    // Mock fetch, confirm, alert, et la pagination globale
    global.fetch = jest.fn(() => Promise.resolve({ ok: true }));
    global.confirm = jest.fn(() => true);
    global.alert = jest.fn();
    window.globalPagination = { refreshPagination: jest.fn() };
    document.dispatchEvent(new Event("DOMContentLoaded"));
  });

  afterEach(() => {
    jest.resetAllMocks();
    sessionStorage.clear();
  });

  it("envoie un DELETE au bon endpoint et supprime la ligne", async () => {
    // Simule le clic sur le bouton
    btn.click();
    // Attend la fin de l'event loop pour que l'async soit traité
    await new Promise(r => setTimeout(r, 0));
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:5000/api/event/42",
      expect.objectContaining({
        method: "DELETE",
        headers: expect.objectContaining({
          "Authorization": "Bearer fake-token"
        })
      })
    );
    expect(window.globalPagination.refreshPagination).toHaveBeenCalled();
    expect(document.querySelectorAll("tr").length).toBe(0);
  });

  it("affiche une alerte si la suppression échoue", async () => {
    global.fetch.mockResolvedValueOnce({ ok: false });
    btn.click();
    await new Promise(r => setTimeout(r, 0));
    expect(global.alert).toHaveBeenCalledWith("Erreur lors de la suppression !");
    expect(document.querySelectorAll("tr").length).toBe(1);
  });

  it("ne fait rien si confirm est annulé", async () => {
    global.confirm.mockReturnValueOnce(false);
    btn.click();
    await new Promise(r => setTimeout(r, 0));
    expect(global.fetch).not.toHaveBeenCalled();
    expect(document.querySelectorAll("tr").length).toBe(1);
  });
});
