import { For, Show, type JSXElement } from "solid-js";
import "./site-footer.css";

export type FooterLink = { label: string; href: string };
export type FooterColumn = { title: string; links: FooterLink[] };

export type SiteFooterProps = {
  brand: string;
  acknowledgement?: string;
  columns: FooterColumn[];
  legalLinks?: FooterLink[];
  copyright?: string;
  socialLinks?: Array<{ label: string; href: string; icon?: JSXElement }>;
  paymentLabels?: string[];
  class?: string;
};

export function SiteFooter(props: SiteFooterProps) {
  return (
    <footer class={["sf", props.class].filter(Boolean).join(" ")}>
      <div class="sf__top">
        <div class="sf__brand">
          <p class="sf__logo">{props.brand}</p>
          <Show when={props.acknowledgement}>
            <p class="sf__ack">{props.acknowledgement}</p>
          </Show>
          <Show when={props.socialLinks && props.socialLinks.length > 0}>
            <ul class="sf__social">
              <For each={props.socialLinks!}>
                {(item) => (
                  <li>
                    <a href={item.href} aria-label={item.label}>
                      {item.icon ?? item.label}
                    </a>
                  </li>
                )}
              </For>
            </ul>
          </Show>
        </div>

        <div class="sf__columns">
          <For each={props.columns}>
            {(col) => (
              <div class="sf__column">
                <p class="sf__col-title">{col.title}</p>
                <ul>
                  <For each={col.links}>
                    {(link) => (
                      <li>
                        <a href={link.href}>{link.label}</a>
                      </li>
                    )}
                  </For>
                </ul>
              </div>
            )}
          </For>
        </div>
      </div>

      <div class="sf__bottom">
        <div class="sf__legal">
          <span>{props.copyright ?? `© ${new Date().getFullYear()} ${props.brand}`}</span>
          <Show when={props.legalLinks}>
            <For each={props.legalLinks!}>
              {(link) => (
                <a href={link.href}>{link.label}</a>
              )}
            </For>
          </Show>
        </div>
        <Show when={props.paymentLabels}>
          <ul class="sf__payments" aria-label="Accepted payment methods">
            <For each={props.paymentLabels!}>{(label) => <li>{label}</li>}</For>
          </ul>
        </Show>
      </div>
    </footer>
  );
}

export default SiteFooter;
