require 'imports/http/enums'

local HTTP = {}

function HTTP:new()
    local o = setmetatable({}, self)

    self.__index = self
    self.__name = "HTTP"

    return o
end

function HTTP:send(http_request)
    return SendHTTPRequest(
        http_request.method, 
        http_request.url, 
        http_request.body, 
        http_request.auth,
        http_request.payload,
        http_request.headers,
        http_request.cookies,
        http_request.timeout
    )
end

return HTTP