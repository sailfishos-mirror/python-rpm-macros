-- Convenience Lua functions that can be used within Python srpm/rpm macros

-- Determine alternate names provided from the given name.
-- Used in pythonname provides generator, python_provide and py_provides.
-- There are 2 rules:
--  python3-foo  -> python-foo, python3X-foo
--  python3X-foo -> python-foo, python3-foo
-- There is no python-foo -> rule, python-foo packages are version agnostic.
-- Returns a table/array with strings. Empty when no rule matched.
local function python_altnames(name)
  local xy = rpm.expand('%{__default_python3_pkgversion}')
  local altnames = {}
  local replaced
  -- NB: dash needs to be escaped!
  if name:match('^python3%-') then
    for i, prefix in ipairs({'python-', 'python' .. xy .. '-'}) do
      replaced = name:gsub('^python3%-', prefix)
      table.insert(altnames, replaced)
    end
  elseif name:match('^python' .. xy .. '%-') then
    for i, prefix in ipairs({'python-', 'python3-'}) do
      replaced = name:gsub('^python' .. xy .. '%-', prefix)
      table.insert(altnames, replaced)
    end
  end
  return altnames
end


return {
  python_altnames = python_altnames,
}
