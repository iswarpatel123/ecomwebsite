import { For, Show, type JSXElement } from "solid-js";
import { NavDropdown, type NavDropdownItem } from "../nav-dropdown/NavDropdown";
import "./site-header.css";

export type SiteHeaderNavItem = {
  label: string;
  href: string;
  /** When set, renders a subcategory dropdown for this tab. */
  children?: NavDropdownItem[];
  /** Dropdown layout override. */
  dropdownVariant?: "list" | "cards";
  /** Mega-menu heading override. */
  dropdownTitle?: string;
  shopAllLabel?: string;
};

export type SiteHeaderProps = {
  brand: string;
  brandHref?: string;
  navItems: SiteHeaderNavItem[];
  /** Marks the matching nav item as current (pathname or full href). */
  activeHref?: string;
  /** Prefer this when multiple items share one href (match by label). */
  activeLabel?: string;
  /** Slot replacing the brand wordmark. */
  renderBrand?: () => JSXElement;
  /** Optional trailing utilities slot (search/cart later). */
  renderActions?: () => JSXElement;
  class?: string;
  id?: string;
};

/**
 * Primary storefront header: brand + category nav.
 * Nav items may include `children` for subcategory dropdowns.
 */
export function SiteHeader(props: SiteHeaderProps) {
  const brandHref = () => props.brandHref ?? "/";
  const isActive = (item: SiteHeaderNavItem) => {
    if (props.activeLabel) return item.label === props.activeLabel;
    const active = props.activeHref;
    if (!active) return false;
    return active === item.href || active.startsWith(`${item.href}/`);
  };

  return (
    <header id={props.id} class={["sh", props.class].filter(Boolean).join(" ")}>
      <div class="sh__inner">
        <Show when={props.renderBrand} fallback={
          <a class="sh__brand" href={brandHref()} aria-label={`${props.brand} home`}>
            {props.brand}
          </a>
        }>
          {props.renderBrand!()}
        </Show>

        <nav class="sh__nav" aria-label="Primary">
          <ul class="sh__list">
            <For each={props.navItems}>
              {(item) => (
                <li class="sh__item">
                  <Show
                    when={item.children && item.children.length > 0}
                    fallback={
                      <a
                        href={item.href}
                        class="sh__link"
                        classList={{ "is-active": isActive(item) }}
                        aria-current={isActive(item) ? "page" : undefined}
                      >
                        {item.label}
                      </a>
                    }
                  >
                    <NavDropdown
                      label={item.label}
                      href={item.href}
                      items={item.children!}
                      variant={item.dropdownVariant}
                      panelTitle={item.dropdownTitle}
                      shopAllHref={item.href}
                      shopAllLabel={item.shopAllLabel}
                      active={isActive(item)}
                      align="center"
                      class="sh__dropdown"
                    />
                  </Show>
                </li>
              )}
            </For>
          </ul>
        </nav>

        <Show when={props.renderActions}>
          <div class="sh__actions">{props.renderActions!()}</div>
        </Show>
      </div>
    </header>
  );
}

export default SiteHeader;
