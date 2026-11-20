-- Minimal stand-ins for Quarto features so the book can be previewed with plain pandoc:
-- figure numbering, @fig- cross-references, and callout blocks (collapse="true" -> <details>).
-- Quarto renders the same source natively; this filter is only for the pandoc preview.
local fignum, n = {}, 0

local function number_figures(doc)
  doc = doc:walk({
    Figure = function(f)
      if f.identifier:match("^fig%-") then
        n = n + 1
        fignum[f.identifier] = n
        local cap = f.caption.long
        if #cap > 0 and cap[1].t == "Plain" then
          table.insert(cap[1].content, 1, pandoc.Space())
          table.insert(cap[1].content, 1, pandoc.Strong({pandoc.Str("Figure " .. n .. ".")}))
        end
        f.caption.long = cap
      end
      return f
    end
  })
  return doc:walk({
    Cite = function(c)
      local id = c.citations[1].id
      if fignum[id] then
        return pandoc.Link({pandoc.Str("Figure " .. fignum[id])}, "#" .. id)
      end
    end
  })
end

local function callouts(div)
  local kind = nil
  for _, cl in ipairs(div.classes) do
    local k = cl:match("^callout%-(%a+)$")
    if k then kind = k end
  end
  if not kind then return nil end
  local title = div.attributes["title"] or (kind:gsub("^%l", string.upper))
  if div.attributes["collapse"] == "true" then
    local out = { pandoc.RawBlock("html", '<details class="callout callout-' .. kind .. '"><summary>' .. title .. "</summary>") }
    for _, b in ipairs(div.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock("html", "</details>"))
    return out
  end
  local head = pandoc.Div({pandoc.Plain({pandoc.Strong({pandoc.Str(title)})})}, {class = "callout-title"})
  table.insert(div.content, 1, head)
  div.classes = {"callout", "callout-" .. kind}
  return div
end

return {
  { Pandoc = number_figures },
  { Div = callouts },
}
