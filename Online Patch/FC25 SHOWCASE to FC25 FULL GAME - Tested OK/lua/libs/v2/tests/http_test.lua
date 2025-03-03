json = require 'imports/external/json'

-- Test my http library

-- Local variables
local payload = {}
local cookies = {}
local headers = {}

local req = REQUEST:new({
    method = HTTP_GET_REQUEST,
    url = "https://example.com/",
    timeout = 10000 -- 1s
})

------------- GET Requests -------------

-- Simple Get
local resp1 = HTTP:send(req)
assert(resp1.status_code == 200, string.format("resp1 status_code %d != 200", resp1.status_code))

-- Cookies
req:Clear()
req:SetMethod(HTTP_GET_REQUEST)
req:SetUrl("http://www.httpbin.org/cookies/set?cookies=yummy")
req:SetTimeout(50000)   -- 5s

local resp2 = HTTP:send(req)
assert(resp2.status_code == 200, string.format("resp2 status_code %d != 200", resp2.status_code))
assert(resp2.cookies.cookies == "yummy", string.format("resp2.cookies != yummy"))

cookies = { 
   ["cookie1_key"] = "cookie1_val", 
   ["cookie2_key"] = "cookie2_val"
}
req:SetCookies(cookies)
local resp3 = HTTP:send(req)
assert(resp3.status_code == 200, string.format("resp3 status_code %d != 200", resp3.status_code))

-- Convert response text to json
local resp3_json = json.decode(resp3.text)
assert(resp3_json.cookies.cookie1_key == "cookie1_val", string.format("resp3_json.cookies.cookie1_key != cookie1_val"))
assert(resp3_json.cookies.cookie2_key == "cookie2_val", string.format("resp3_json.cookies.cookie2_key != cookie2_val"))

-- User Agent
headers = {
    ["user-agent"] = "FC Live Editor"
}

req:Clear()
req:SetMethod(HTTP_GET_REQUEST)
req:SetCookies(cookies)
req:SetHeaders(headers)
req:SetUrl("http://httpbin.org/user-agent")
local resp4 = HTTP:send(req)
assert(resp4.status_code == 200, string.format("resp4 status_code %d != 200", resp4.status_code))

local resp4_json = json.decode(resp4.text)
assert(resp4_json["user-agent"] == "FC Live Editor", string.format("resp4_json.user-agent != FC Live Editor"))


-- Auth
req:Clear()
req:SetMethod(HTTP_GET_REQUEST)

local basic_auth = {
    ["username"] = "user",
    ["password"] = "pass",
    ["auth_mode"] = HTTP_AUTH_METHOD_BASIC
}

req:SetAuth(basic_auth)
req:SetUrl("http://www.httpbin.org/basic-auth/user/pass")
local resp7 = HTTP:send(req)
assert(resp7.status_code == 200, string.format("resp7 status_code %d != 200", resp7.status_code))
local resp7_json = json.decode(resp7.text)
assert(resp7_json.authenticated, string.format("resp7 not authenticated"))

local digest_auth = {
    ["username"] = "user",
    ["password"] = "pass",
    ["auth_mode"] = HTTP_AUTH_METHOD_DIGEST
}
req:SetAuth(digest_auth)
req:SetUrl("http://www.httpbin.org/digest-auth/auth/user/pass")
local resp8 = HTTP:send(req)
assert(resp8.status_code == 200, string.format("resp8 status_code %d != 200", resp8.status_code))
local resp8_json = json.decode(resp8.text)
assert(resp8_json.authenticated, string.format("resp8 not authenticated"))

local bearer_token_auth = {
    ["access_token"] = "ACCESS_TOKEN",
    ["auth_mode"] = HTTP_AUTH_METHOD_BEARER
}
req:SetAuth(bearer_token_auth)
req:SetUrl("http://www.httpbin.org/bearer")
local resp9 = HTTP:send(req)
assert(resp9.status_code == 200, string.format("resp9 status_code %d != 200", resp9.status_code))
local resp9_json = json.decode(resp9.text)
assert(resp9_json.authenticated, string.format("resp9 not authenticated"))

------------- POST Requests -------------

payload = {
    ["some key"] = "some value",
    ["another key"] = "another value"
}

req:Clear()
req:SetMethod(HTTP_POST_REQUEST)
req:SetPayload(payload)
req:SetUrl("http://httpbin.org/post")

local resp5 = HTTP:send(req)
assert(resp5.status_code == 200, string.format("resp5 status_code %d != 200", resp5.status_code))
local resp5_json = json.decode(resp5.text)
assert(resp5_json.form["some key"] == "some value", string.format("resp5_json.some key != some value"))
assert(resp5_json.form["another key"] == "another value", string.format("resp5_json.another key != another value"))

-- Raw body
headers = {
    ["Content-Type"] = "text/plain"
}

req:Clear()
req:SetMethod(HTTP_POST_REQUEST)
req:SetHeaders(headers)
req:SetBody("This is a raw body")
req:SetUrl("http://httpbin.org/post")

local resp6 = HTTP:send(req)
assert(resp6.status_code == 200, string.format("resp6 status_code %d != 200", resp6.status_code))
local resp6_json = json.decode(resp6.text)
assert(resp6_json.data == "This is a raw body", string.format("resp6_json.data != This is a raw body"))

