import { For, Show, createEffect, createSignal, onCleanup, type JSXElement } from "solid-js";
import "./nav-dropdown.css";

export type NavDropdownItem = {
  id: string;
  label: string;
  href: string;
  /** Optional thumbnail for card-style menus. */
  imageSrc?: string;
  imageAlt?: string;
};

export type NavDropdownProps = {
  label: string;
  /** Optional destination for the trigger label itself. */
  href?: string;
  items: NavDropdownItem[];
  /** `cards` shows image+label tiles; `list` is text links. Default: cards if any item has imageSrc. */
  variant?: "list" | "cards";
  /** Open on pointer enter. Default true. */
  openOnHover?: boolean;
  align?: "start" | "center" | "end";
  active?: boolean;
  class?: string;
  id?: string;
  renderTrigger?: () => JSXElement;
  renderItem?: (item: NavDropdownItem) => JSXElement;
};

/**
 * Reusable nav dropdown for category / subcategory menus.
 * Cards variant is a full-bleed mega menu with equal-width columns.
 */
export function NavDropdown(props: NavDropdownProps) {
  const [open, setOpen] = createSignal(false);
  const [panelTop, setPanelTop] = createSignal(0);
  let rootEl: HTMLDivElement | undefined;
  let closeTimer = 0;

  const variant = () => {
    if (props.variant) return props.variant;
    return props.items.some((item) => item.imageSrc) ? "cards" : "list";
  };

  const hoverEnabled = () => props.openOnHover !== false;
  const panelId = () => props.id ?? `nav-dd-${props.label.replace(/\s+/g, "-").toLowerCase()}`;
  const cols = () => Math.max(1, Math.min(props.items.length, 8));

  const syncPanelPosition = () => {
    if (typeof window === "undefined" || !rootEl || variant() !== "cards") return;
    const rect = rootEl.getBoundingClientRect();
    setPanelTop(Math.round(rect.bottom));
  };

  const openMenu = () => {
    clearTimeout(closeTimer);
    syncPanelPosition();
    setOpen(true);
  };

  const scheduleClose = () => {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => setOpen(false), 140) as unknown as number;
  };

  const toggle = () => {
    if (open()) setOpen(false);
    else openMenu();
  };

  const onDocPointer = (event: PointerEvent) => {
    if (!open()) return;
    const target = event.target as Node | null;
    if (rootEl && target && !rootEl.contains(target)) setOpen(false);
  };

  const onKey = (event: KeyboardEvent) => {
    if (event.key === "Escape") setOpen(false);
  };

  createEffect(() => {
    if (typeof document === "undefined") return;
    if (!open()) return;
    syncPanelPosition();
    document.addEventListener("pointerdown", onDocPointer);
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", syncPanelPosition);
    window.addEventListener("scroll", syncPanelPosition, true);
    onCleanup(() => {
      document.removeEventListener("pointerdown", onDocPointer);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", syncPanelPosition);
      window.removeEventListener("scroll", syncPanelPosition, true);
    });
  });

  onCleanup(() => clearTimeout(closeTimer));

  return (
    <div
      ref={(el) => {
        rootEl = el;
      }}
      class={["nd", props.class].filter(Boolean).join(" ")}
      classList={{
        "is-open": open(),
        "is-active": !!props.active,
        [`nd--${variant()}`]: true,
        [`nd--align-${props.align ?? "center"}`]: true,
      }}
      style={{ "--nd-cols": String(cols()) }}
      onPointerEnter={() => {
        if (hoverEnabled()) openMenu();
      }}
      onPointerLeave={() => {
        if (hoverEnabled()) scheduleClose();
      }}
    >
      <Show
        when={props.renderTrigger}
        fallback={
          <Show
            when={props.href}
            fallback={
              <button
                type="button"
                class="nd__trigger"
                aria-expanded={open()}
                aria-haspopup="true"
                aria-controls={panelId()}
                onClick={toggle}
              >
                <span>{props.label}</span>
                <span class="nd__chevron" aria-hidden="true" />
              </button>
            }
          >
            <a
              href={props.href}
              class="nd__trigger nd__trigger--link"
              aria-expanded={open()}
              aria-haspopup="true"
              aria-controls={panelId()}
              onClick={(e) => {
                const touchLike =
                  typeof window !== "undefined" && window.matchMedia("(hover: none)").matches;
                if (!hoverEnabled() || touchLike) {
                  e.preventDefault();
                  toggle();
                }
              }}
            >
              <span>{props.label}</span>
              <span class="nd__chevron" aria-hidden="true" />
            </a>
          </Show>
        }
      >
        <div
          class="nd__trigger-slot"
          onClick={toggle}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              toggle();
            }
          }}
          role="button"
          tabIndex={0}
          aria-expanded={open()}
          aria-haspopup="true"
          aria-controls={panelId()}
        >
          {props.renderTrigger!()}
        </div>
      </Show>

      <Show when={open()}>
        <div
          id={panelId()}
          class="nd__panel"
          role="menu"
          style={variant() === "cards" ? { top: `${panelTop()}px` } : undefined}
          onPointerEnter={openMenu}
          onPointerLeave={() => {
            if (hoverEnabled()) scheduleClose();
          }}
        >
          <div class="nd__panel-inner">
            <ul
              class="nd__items"
              classList={{
                "nd__items--cards": variant() === "cards",
                "nd__items--list": variant() === "list",
              }}
            >
              <For each={props.items}>
                {(item) => (
                  <li role="none">
                    <Show
                      when={props.renderItem}
                      fallback={<DefaultItem item={item} variant={variant()} onNavigate={() => setOpen(false)} />}
                    >
                      {props.renderItem!(item)}
                    </Show>
                  </li>
                )}
              </For>
            </ul>
          </div>
        </div>
      </Show>
    </div>
  );
}

function DefaultItem(props: { item: NavDropdownItem; variant: "list" | "cards"; onNavigate: () => void }) {
  return (
    <a class="nd__item" href={props.item.href} role="menuitem" onClick={() => props.onNavigate()}>
      <Show when={props.variant === "cards" && props.item.imageSrc}>
        <span class="nd__thumb">
          <img src={props.item.imageSrc} alt={props.item.imageAlt ?? ""} loading="lazy" decoding="async" />
        </span>
      </Show>
      <span class="nd__label">{props.item.label}</span>
    </a>
  );
}

export default NavDropdown;
