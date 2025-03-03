require 'imports/http/enums'

local REQUEST = {}

function REQUEST:new(init)
    local o = setmetatable({}, self)

    if (init == nil) then
        init = {}
    end

    self.__index = self
    self.__name = "REQUEST"

    self.method = init.method or HTTP_GET_REQUEST
    self.url = init.url or "https://example.com/"
    self.body = init.body or ""

    self.auth = init.auth or {}
    self.payload = init.payload or {}
    self.headers = init.headers or {}
    self.cookies = init.cookies or {}

    self.timeout = init.timeout or 0

    return o
end

function REQUEST:Clear()
	self.method = HTTP_GET_REQUEST
    self.url = "https://example.com/"
    self.body = ""

    self.auth = {}
    self.payload = {}
    self.headers = {}
    self.cookies = {}

    self.timeout = 0
end

function REQUEST:SetMethod(method)
	self.method = method
end

function REQUEST:SetUrl(url)
	self.url = url
end

function REQUEST:SetAuth(auth)
	self.auth = auth
end

function REQUEST:SetBody(body)
	self.body = body
end

function REQUEST:SetPayload(payload)
	self.payload = payload
end

function REQUEST:SetHeaders(headers)
	self.headers = headers
end

function REQUEST:SetCookies(cookies)
	self.cookies = cookies
end

function REQUEST:SetTimeout(timeout)
	self.timeout = timeout
end

return REQUEST